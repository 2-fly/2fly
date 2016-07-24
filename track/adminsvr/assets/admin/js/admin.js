QUERY_BTN = "query campaign";

$.fn.InitDomainInputCompent = function(p) {
    var step = 2;
    if(!p) p = {};
    var btn_txt = p.btn_txt ? p.btn_txt:"Add",
        name = this.attr("id"),
        dest = p.dest ?p.dest:"",
        input_filter = $("<div style='margin-bottom:10px'><label class='radio inline'>display : </label></div>"),
        input_container = $("<div class='input-container'></div>"),
        that = this,
        btn_div = $("<div style='width:220px;padding-top:10px'></div>"),
        add_btn = $("<button type=button uid='"+ i + "' style='display:block;margin:10px 0 0'>"+ btn_txt+ "</button>"),
        modal = $('<div id="modal_'+name+'" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">\
          <div class="modal-header">\
            <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>\
            <h3 id="myModalLabel">Add '+name+' Domains</h3>\
          </div>\
          <div class="modal-body">\
            <textarea style="width:90%;height:300px"></textarea>\
          </div>\
          <div class="modal-footer">\
            <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>\
            <button type="button" id="add_'+name+'_domain" class="btn btn-primary">Add</button>\
          </div>\
        </div>'),
        clear = $("<div style='clear:both'></div>");
    input_filter = input_filter.appendTo(this);
    input_container = input_container.appendTo(this);
    btn_div.append(add_btn);
    btn_div.append(modal);
    btn_div.append(clear);
    this.append(btn_div);

    input_filter.append('<label class="radio inline"><input name="filter_'+name+'" type="radio" value="all" checked>all</label>');
    input_filter.append('<label class="radio inline"><input name="filter_'+name+'" type="radio" value="good">good</label>');
    input_filter.append('<label class="radio inline"><input name="filter_'+name+'" type="radio" value="bad">bad</label>');
    input_filter.append('<label class="radio inline"><input name="filter_'+name+'" type="radio" value="hidden">hidden</label>');
    input_filter.append('<label class="radio inline"><input name="filter_'+name+'" type="radio" value="show">show</label>');
    input_filter.append('<label class="radio inline"><input name="filter_'+name+'" type="radio" value="using">using</label>');
    input_filter.append('<label class="radio inline"><input name="filter_'+name+'" type="radio" value="not_using">not using</label>');

    modal.on('hidden', function() {$(this).find("textarea").val("")});
    $("#add_"+name+"_domain").click(function() {
        var domains = modal.find("textarea").val();
        domains = domains.split("\n");
        for(var i in domains) {
            var domain = domains[i];
            that._add_domain(domain, 0, {});
        }
        $("#modal_"+name).modal('toggle');
    });
    add_btn.kendoButton({
        spriteCssClass: "k-icon k-i-plus",
        click: function () {
            $("#modal_"+name).modal('toggle')
        },
    });

    if(!p.data) {
        p.data = [];
    } else {
        var data = p.data.split(",");
        p.data = $.map(data, function(item) {
            var r = item.split(";");
            if(r.length == 1)
                r.push("0")
            return r;
        });
    }

    $.extend(this, {
        _init_display_radio:function(select) {
            $(select).change(function() {
                switch($(this).val()) {
                    case "good":
                        input_container.children().each(function(i, v) {
                            var e = $(v).children(),
                                notice = e[e.length-1];
                            if($(notice).hasClass("label-success")){
                                $(v).show();
                            } else {
                                $(v).hide();
                            };
                        });
                        break;
                    case "bad":
                        input_container.children().each(function(i, v) {
                            var e = $(v).children(),
                                notice = e[e.length-1];
                            if($(notice).hasClass("label-success")){
                                $(v).hide();
                            } else {
                                $(v).show();
                            };
                        });
                        break;
                    case "hidden":
                        input_container.children().each(function(i, v) {
                            if($(v).attr("show") == undefined){
                                $(v).show();
                            } else {
                                $(v).hide();
                            };
                        });
                        break;
                    case "show":
                        input_container.children().each(function(i, v) {
                            if($(v).attr("show") != undefined){
                                $(v).show();
                            } else {
                                $(v).hide();
                            };
                        });
                        break;
                    case "using":
                        input_container.children().each(function(i, v) {
                            var text = $(v).find("button").text();
                            if(text == QUERY_BTN) {
                                $(v).hide();
                            } else {
                                $(v).show();
                            }
                        });
                        break;
                    case "not_using":
                        input_container.children().each(function(i, v) {
                            var text = $(v).find("button").text();
                            if(text == QUERY_BTN) {
                                $(v).show();
                            } else {
                                $(v).hide();
                            }
                        });
                        break;
                    default:
                        input_container.children().each(function(i, v) {
                            $(v).show();
                        });
                }
            });
        },
        has_check:p.has_check,
        VerifyRes:function(res) {
            var container = this.find(".input-container");
            container.find("input[type='text']").each(function(i, v) {
                var val = res[$(v).val()];
                $(v).removeAttr("readonly");
                if(val != undefined) {
                    var ns_list = [];
                    for(var i in val.ns) {
                        var space = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                        ns_list.push([space, space, val.ns[i]].join(""));
                    }
                    if(ns_list.length) {
                        ns_list[0] = val.ret + ns_list[0].slice(parseInt(val.ret.length)*12);
                        var text = ns_list.join("<br>");
                    } else {
                        var text = val.ret;
                    }
                    var p = $(v).nextAll('div');
                    if (val.ret == "Success") {
                        if(p.hasClass("label-important")) {
                           p.removeClass("label-important");
                           p.addClass("label-success");
                        }
                    } else {
                        if(p.hasClass("label-success")) {
                           p.removeClass("label-success");
                           p.addClass("label-important");
                        }
                    }

                    p.html(text);

                }
            });
        },
        Res:function(res) {
            this.find("input[type='text']").each(function(i, v) {
                var text = res[$(v).val()];
                $(v).removeAttr("readonly");
                if(text != undefined) {
                    var p = $(v).nextAll('div');
                    if (text.indexOf("good") == 0) {
                        if(p.hasClass("label-important")) {
                           p.removeClass("label-important");
                           p.addClass("label-success");
                        }
                    } else {
                        if(p.hasClass("label-success")) {
                           p.removeClass("label-success");
                           p.addClass("label-important");
                        }
                    }
                    p.html(text);
                }
            });
        },

        VirusRes:function(res) {
            this.find("input[type='text']").each(function(i, v) {
                var val = res[$(v).val()];
                $(v).removeAttr("readonly");
                if(val != undefined) {
                    text=val.ret;
                    var p = $(v).nextAll('div');
                    if (text.indexOf("good") == 0) {
                        if(p.hasClass("label-important")) {
                           p.removeClass("label-important");
                           p.addClass("label-success");
                        }
                    } else {
                        if(p.hasClass("label-success")) {
                           p.removeClass("label-success");
                           p.addClass("label-important");
                        }
                    }

                    p.html(text);

                }
            });
        },

        GetValue:function() {
            var container = this.find(".input-container"),
                v_list = [],
                r_list = [],
                ret = {ret:true};
            container.find("p").each(function(i, v) {
                $(v).text("");
            });
            container.find("input[type='text']").each(function(i, v) {
                var val = $(v).val();
                if(val.length==0) {
                    return true;
                }
                v_list.push([val, $(v).parent().attr("show") == undefined? 1:0]);
            });
            if(!ret.ret)
                return ret;

            for(var i in v_list) {
                r_list.push(v_list[i][0]+";"+v_list[i][1]);
            }

            return {ret:true,data:r_list.join(",")};
        },
        Hide:function() {
            this.find("input[type='checkbox']:checked").each(function(i, v) {
                if(!$(v).parent().is(":hidden")) {
                    that._hide($(v).parent());
                }
            });
        },
        _hide:function(p, init) {
            p.removeAttr("show");
            if($(that).find("input:radio:checked").val() == "show") {
                p.hide();
            }
        },
        Show:function() {
            this.find("input[type='checkbox']:checked").each(function(i, v) {
                if(!$(v).parent().is(":hidden")) {
                    $(v).parent().attr("show", "");
                    if($(that).find("input:radio:checked").val() == "hidden") {
                        $(v).parent().hide();
                    }
                }
            });
        },
        SelectAll:function() {
            input_container.children().each(function(i, v) {
                var checkbox = $($(v).find("input[type=checkbox]"));
                if(!$(checkbox).is(":checked")) {
                    $(checkbox).click();
                }
            })
        },
        CancelAll:function() {
            input_container.children().each(function(i, v) {
                var checkbox = $($(v).find("input[type=checkbox]"));
                if($(checkbox).is(":checked")) {
                    $(checkbox).click();
                }
            })
        },
        _add_domain:function(domain, hidden, camps) {
            var display_val = $(that).find("input:radio:checked").val(),
                display = "";
            if(display_val != "all" && display_val != "bad" && display_val != "show" && display_val != "not_using") {
                display = "style='display:none'";
            }
            var input_obj = $("<div class='row-fluid' show "+display+"></div>"),
                input = $("<input type='text' value='"+ domain +"'>"),
                error = '<div id="comfirn-err" class="label label-important" style="margin-left:10px"></div>',
                close_btn = $('<a href="#" class="my-container icon-remove icon"></a>');
            if(p.has_check) {
                input_obj.append("<input type='checkbox' style='margin-right:10px'>");
            }
            input_obj.append(input);
            if(p.query_field) {
                var camp_num = camps[domain]?"("+camps[domain]+")":"";
                var btn = $("<button type='button' style='margin-left:10px'>"+QUERY_BTN+camp_num+"</button>");
                input_obj.append(btn);
                btn.kendoButton({});
                btn.click(function() {
                    var domain = $(this).prevAll("input[type='text']").val();
                    open(p.query_url + "?"+p.query_field+"=" + domain);
                });
            }

            input_obj.append(close_btn);
            input_obj.append(error);
            input_container.append(input_obj);
            if(parseInt(hidden)) { this._hide(input_obj, true);}
            close_btn.click(function() {
                var domain = $(this).prevAll("input[type='text']").val();
                if(domain.length == 0) {
                    var r = true;
                } else {
                    var r = confirm("Are you sure delete "+domain+"?");
                }
                if(r==true) {
                    $(this).closest("div").remove();
                    $("#"+dest).val(that.GetValue());
                }
                return false;
            });
        },
    });
    this._init_display_radio("input:radio[name=filter_"+name+"]");
    var camps = p.camp?p.camp:{};
    for(var i = 0; i < p.data.length; i+=step) {
        this._add_domain(p.data[i], p.data[i+1], camps);
    }

    return this;
}

$.fn.InitAddInputCompent = function(p) {
    var step = 2;
    if(!p) p = {};
    var btn_txt = p.btn_txt ? p.btn_txt:"Add",
        dest = p.dest ?p.dest:"",
        input_container = $("<div class='input-container'></div>"),
        that = this,
        show_link = $("<a style='cursor:pointer'>show all</a>"),
        btn_div = $("<div style='width:220px;padding-top:10px'></div>"),
        add_btn = $("<button type=button uid='"+ i + "' style='display:block;margin:10px 0 0'>"+ btn_txt+ "</button>"),
        clear = $("<div style='clear:both'></div>");

    input_container = input_container.appendTo(this);
    btn_div.append(show_link);
    btn_div.append(add_btn);
    btn_div.append(clear);
    this.append(btn_div);

    show_link.click(function() {
        if($(this).attr("show")) {
            input_container.children().each(function(i, v) {
                var input = $(v).children("input[type='text']")
                if (input.attr('hidden'))
                    $(v).hide();
            });
            $(this).removeAttr("show");
            $(this).text("show all");
        } else {
            input_container.children().each(function(i, v) {
                $(v).show();
            });
            $(this).attr("show", "show");
            $(this).text("hide");
        }
    });

    add_btn.kendoButton({
        spriteCssClass: "k-icon k-i-plus",
        click: function () {
            var input_obj = $("<div class='row-fluid'></div>"),
                input = $("<input type='text' >"),
                close_btn = $('<a href="#" class="my-container icon-remove icon"></a>'),
                error = '<div id="comfirn-err" class="label label-important" style="margin-left:10px"></div>';

            if(p.has_check) {
                input_obj.append("<input type='checkbox' style='margin-right:10px'/>");
            }
            input_obj.append(input);
            if(p.query_field) {
                var btn = $("<button type='button' style='margin-left:10px'>"+QUERY_BTN+"</button>");
                input_obj.append(btn);
                btn.kendoButton({});
                btn.click(function() {
                    var domain = $(this).prevAll("input[type='text']").val();
                    open(p.query_url + "?" + query_field + "=" + domain);
                });
            }

            input_obj.append(close_btn);
            input_obj.append(error);
            input_container.append(input_obj);
            close_btn.click(function() {
                var domain = $(this).prevAll("input[type='text']").val();
                if(domain.length == 0) {
                    var r = true;
                } else {
                    var r = confirm("Are you sure delete "+domain+"?");
                }
                if(r==true) {
                    $(this).closest("div").remove();
                    $("#"+dest).val(that.GetValue());
                }
                return false;
            });
        },
    });

    if(!p.data) {
        p.data = "";
    }
    var data = p.data.split(",");
    p.data = $.map(data, function(item) {
        var r = item.split(";");
        if(r.length == 1)
            r.push("0")
        return r;
    });

    var camps = p.camp?p.camp:{};
    for(var i = 0; i < p.data.length; i+=step) {

        var input_obj = $("<div class='row-fluid'></div>"),
            input = $("<input type='text' value='"+ p.data[i] +"'>"),
            error = '<div id="comfirn-err" class="label label-important" style="margin-left:10px"></div>',
            close_btn = $('<a href="#" class="my-container icon-remove icon"></a>');
        if(p.has_check) {
            input_obj.append("<input type='checkbox' style='margin-right:10px'>");
        }
        input_obj.append(input);
        if(p.query_field) {
            var camp_num = camps[p.data[i]]?"("+camps[p.data[i]]+")":"";
            var btn = $("<button type='button' style='margin-left:10px'>"+ QUERY_BTN +camp_num+"</button>");
            input_obj.append(btn);
            btn.kendoButton({});
            btn.click(function() {
                var domain = $(this).prevAll("input[type='text']").val();
                open(p.query_url + "?"+p.query_field+"=" + domain);
            });
        }

        var hide_btn = $("<button type='button' style='margin-left:10px'>hide</button>");
        input_obj.append(hide_btn);
        hide_btn.kendoButton({});
        hide_btn.click(function() {
            var input = $(this).prevAll("input[type='text']");
            if(input.attr("hidden")) {
                $(this).removeClass("hide-btn-bg");
                input.removeAttr("hidden");
                $(this).text("hide");
                $(this).parent().show();
            } else {
                input.attr("hidden", "hidden");
                $(this).addClass("hide-btn-bg")
                $(this).text("show");
                var show_link = $(this).parent().parent().next().children("a");
                if(!show_link.attr("show")) {
                    $(this).parent().hide();
                }
            }
        });
        if(p.data[i+1] != 0)
            hide_btn.click();

        input_obj.append(close_btn);
        input_obj.append(error);
        input_container.append(input_obj);
        close_btn.click(function() {
            var domain = $(this).prevAll("input[type='text']").val();
            if(domain.length == 0) {
                var r = true;
            } else {
                var r = confirm("Are you sure delete "+domain+"?");
            }
            if(r==true) {
                $(this).closest("div").remove();
                $("#"+dest).val(that.GetValue());
            }
            return false;
        });
    }
    $.extend(this, {has_check:p.has_check});
    $.extend(this, {VerifyRes:function(res) {
        var container = this.find(".input-container");
        container.find("input[type='text']").each(function(i, v) {
            var val = res[$(v).val()];
            $(v).removeAttr("readonly");
            if(val != undefined) {
                var ns_list = [];
                for(var i in val.ns) {
                    var space = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                    ns_list.push([space, space, val.ns[i]].join(""));
                }
                if(ns_list.length) {
                    ns_list[0] = val.ret + ns_list[0].slice(parseInt(val.ret.length)*12);
                    var text = ns_list.join("<br>");
                } else {
                    var text = val.ret;
                }
                var p = $(v).nextAll('div');
                if (val.ret == "Success") {
                    if(p.hasClass("label-important")) {
                       p.removeClass("label-important");
                       p.addClass("label-success");
                    }
                } else {
                    if(p.hasClass("label-success")) {
                       p.removeClass("label-success");
                       p.addClass("label-important");
                    }
                }

                p.html(text);

            }
        });
    }});

    $.extend(this, {Res:function(res) {
        this.find("input[type='text']").each(function(i, v) {
            var text = res[$(v).val()];
            $(v).removeAttr("readonly");
            if(text != undefined) {
                var p = $(v).nextAll('div');
                if (text.indexOf("good") == 0) {
                    if(p.hasClass("label-important")) {
                       p.removeClass("label-important");
                       p.addClass("label-success");
                    }
                } else {
                    if(p.hasClass("label-success")) {
                       p.removeClass("label-success");
                       p.addClass("label-important");
                    }
                    $(v).parent().show();
                }
                p.html(text);
            }
        });
    }});

    $.extend(this, {VirusRes:function(res) {
        this.find("input[type='text']").each(function(i, v) {
            var val = res[$(v).val()];
            $(v).removeAttr("readonly");
            if(val != undefined) {
                text=val.ret;
                var p = $(v).nextAll('div');
                if (text.indexOf("good") == 0) {
                    if(p.hasClass("label-important")) {
                       p.removeClass("label-important");
                       p.addClass("label-success");
                    }
                } else {
                    if(p.hasClass("label-success")) {
                       p.removeClass("label-success");
                       p.addClass("label-important");
                    }
                }

                p.html(text);

            }
        });
    }});

    $.extend(this, {GetValue:function() {
        var container = this.find(".input-container"),
            v_list = [],
            r_list = [],
            ret = {ret:true};
        container.find("p").each(function(i, v) {
            $(v).text("");
        });
        container.find("input[type='text']").each(function(i, v) {
            var val = $(v).val();
            if(val.length==0) {
                return true;
            }
            v_list.push([val, $(v).attr("hidden")? 1:0]);
        });
        if(!ret.ret)
            return ret;

        for(var i in v_list) {
            r_list.push(v_list[i][0]+";"+v_list[i][1]);
        }

        return {ret:true,data:r_list.join(",")};
    }});

    $.extend(this, {SelectAll:function() {
        this.find("input[type=checkbox]").each(function(i, v) {
            if(!$(v).is(":checked"))
                $(v).click();
        })
    }});

    $.extend(this, {CancelAll:function() {
        this.find("input[type=checkbox]").each(function(i, v) {
            if($(v).is(":checked"))
                $(v).click();
        })
    }});
    return this;
}

var timeout;
var cur = 0;

function VerifyAll(params) {
    cur += 1;
    clearTimeout(timeout);
    var res_list = [],
        last = [],
        url = params.url,
        max_len_once = params.max_len_once ? params.max_len_once : 30,
        list = params.list;

    for(var i in list) {
        var has_check = list[i].has_check;
        list[i].find("input[type='text']").each(function(i, v) {
            var p = $(v).nextAll('div');
            p.html("");
            var val = $.trim($(v).val());
            if(has_check) {
                var check = $(v).prevAll('input[type="checkbox"]');
                if(!check.is(":checked"))
                    return true;
            }
            if(!val.length) {
                return true;
            }
            $(v).attr("readonly", "readonly");
            var p = $(v).nextAll('div');
            if(p.hasClass("label-success")) {
               p.removeClass("label-success");
               p.addClass("label-important");
            }
            p.text("loading...");
            last.push(val);
            if(last.length >= max_len_once) {
                res_list.push(last);
                last = [];
            }
        });
    }
    if(last.length)
        res_list.push(last);

    if(res_list.length > 0) {
        res_list = $.map(res_list, function(v, i) {
            return v.join(",");
        });

        var n = res_list.length;
        send_msg(res_list, url, cur, 0, res_list.length, params.cb1, params.cb2, params.cb3, params.cb4, list);
    }
}

function send_msg(val_list, url, cur_n, indx, len, cb1, cb2, cb3, cb4, obj_list) {
    cb1();
    timeout = setTimeout(function() {cb3(); clearTimeout(timeout);}, 15000);
    $.ajax({
        type:"POST",
        url:url,
        data:{urls:val_list[indx]},
        success: function(data) {
            if(cur_n != cur)
                return;
            var f = JSON.parse(data);
            $.each(obj_list, function(i, vv) {
                vv[cb4](f);
            });
            if(++indx >= len) {
                cb2();
            } else {
                send_msg(val_list, url, cur_n, indx, len, cb1, cb2, cb3, cb4, obj_list);
            }
        },
        error: function() {
            if(cur_n != cur)
                return;
            var res = {};
            $.each(val_list[indx].split(","), function(i, v) {
                res[v] = {ret:""};
            })
            $.each(obj_list, function(i, vv) {
                vv[cb4](res);
            });
            if(++indx >= len) {
                cb2();
            } else {
                send_msg(val_list, url, cur_n, indx, len, cb1, cb2, cb3, cb4, obj_list);
            }
        }
    });
}


$.fn.InitLoading = function() {
    this.css("display", "none").css("top", "50%").css("left", "50%").css("width", "15%").css("height", "20%").css("position", "absolute").css("text-align", "center");
    this.css("background-color", "rgba(256, 256, 256, 0.1)").css("background-image", "url('/assets/loading.gif')").css("background-repeat", "no-repeat");
    this.css("background-position", "center").css("border", "0px solid white").css("color", "black").css("z-index", "5000");
}

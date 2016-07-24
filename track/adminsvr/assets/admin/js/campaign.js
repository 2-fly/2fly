    var top_cate = {};
    sec_cate = {},
    sec_cate_conf = {},
    sec_cate_url = null,
    add_path_tmp = {type: "add path", text:"Add path"},
    add_rule_tmp = {type: "add rule", text:"Add rule"},
    path_tmp = {type:"path", n:1, text:"Path", value:{}, weight:100, direct_linking:0},
    rule_tmp = {text:"Rule", type:"rule", expanded:true, items:[], value:{}},
    default_swap = {text:"Default paths", expanded:true, type:"normal", items:[]},
    flow_tmp = {text:"New flow", type:"flow"},
    callback = [],
    rule_type_name_container = [],
    click_arg = null;

    function turn_on(id) {
        $("#"+id).removeAttr("readonly");
    }

    function turn_off(id) {
        $("#"+id).attr("readonly", "readonly");
    }

    function getJsonLen(json) {
        var count=0;
        if(!json) return count;
        for(var i in json){
            count++;
        }
        return count;
    }

    function isJsonEmpty(json) {
        if(!json) return true;
        for(var i in json) return false;
        return true;
    }

    function init_rule_type_name(conf) {
        for (var i = 0; i < conf.length; i++) {
            rule_type_name_container.push(conf[i].name);
        }
    }

    function add_collapse(container_name, div_name, content_div_name, close_btn_name, inner_div_name, name, title, node) {
        var collapse = $('<div id="'+div_name+'" class="accordion-group"></div>');
        var head = $('<div class="accordion-heading">');
        var content = $('<div class="accordion-toggle" data-toggle="collapse" data-parent="#'+container_name+'" href="#'+content_div_name+'">\
                <button id="'+close_btn_name+'" type="button" class="close">×</button>\
                '+title+'\
              </div>\
            </div>');
        var btn_radio = $('<div class="btn-radio-group">\
                </div>');

        var btn_is = $('<button type="button" class="btn-radio-is" type="1">is</button>');
        var btn_not = $('<button type="button" class="btn-radio-not" type="0">not</button>');

        content = content.appendTo(head);
        btn_radio = btn_radio.appendTo(content);
        var nbtn_is = btn_is.appendTo(btn_radio);
        var nbtn_not = btn_not.appendTo(btn_radio);

        var body = $('<div id="'+content_div_name+'" class="accordion-body collapse">\
              <div class="accordion-inner" id="'+inner_div_name+'"></div>\
              </div>');
        collapse.append(head);
        collapse.append(body);

        $("#"+container_name).append(collapse);
        if(!click_arg)
            $("#" + content_div_name).collapse("show");

        $("#"+content_div_name).on("hidden", function(e) {
            e.stopPropagation()});

        $("#"+close_btn_name).click(function(e) {
            e.stopPropagation();
            delete node.value[content_div_name]
            $("#"+div_name).remove();
            $("#rule_dropdown_"+name).toggle();

        });
        nbtn_is.unbind("click").click(function(e) {
            e.stopPropagation(e);
            nbtn_is.attr("selected", "selected");
            nbtn_not.removeAttr("selected");
            nbtn_is.removeClass();
            nbtn_is.addClass('btn-radio-is-active');
            nbtn_not.removeClass();
            nbtn_not.addClass('btn-radio-not');
            if(!node.value)
                node.value={};
            if(!node.value[content_div_name])
                node.value[content_div_name] = {};
            node.value[content_div_name].is = 1;
        });


        nbtn_not.unbind("click").click(function(e) {
            nbtn_not.addClass('btn-radio-not-active');
            e.stopPropagation();
            nbtn_not.attr("selected", "selected");
            nbtn_is.removeAttr("selected");
            nbtn_is.removeClass();
            nbtn_is.addClass('btn-radio-is');
            nbtn_not.removeClass();
            nbtn_not.addClass('btn-radio-not-active');
            if(!node.value)
                node.value={};
            if(!node.value[content_div_name]) node.value[content_div_name] = {};
            node.value[content_div_name].is = 0;
        });
        if(node.value && node.value[content_div_name] && !node.value[content_div_name].is)
            nbtn_not.click();
        else
            nbtn_is.click();
    }

    function add_inner_1(content_div_name, inner_div_name) {
        var ul_id = "ul_1_"+content_div_name;
        var ul_2_id = "ul_2_"+content_div_name;
        var ul_3_id = "ul_3_"+content_div_name;
        var inner = '<div class="row-fluid">\
            <div class="span3 border-gray">\
                <input id="search_1_'+content_div_name+'" placeholder="Search" type="text" class="span12" autocomplete="off" role="textbox">\
                <ul class="search_ul" id="'+ul_id+'"></ul>\
            </div>\
            <div class="span3 border-gray">\
                <input id="search_2_'+content_div_name+'" placeholder="Search" type="text" class="span12" autocomplete="off" role="textbox">\
                <ul class="search_ul" id="'+ul_2_id+'"></ul>\
            </div>\
            <div class="span5 border-gray">\
                <ul class="search_ul" id="'+ul_3_id+'" ><ul>\
            </div></div>';
        $("#"+inner_div_name).append(inner);
    }

    function bind_search(search, ul, list, func, args, args_func){
        search.bind("input propertychange", function() {
            ul = $(ul.selector);
            ul.empty();
            if(!$(this).val()) {
                args_func(list, args);
                func.apply(this, args);
            } else {
                var i = 0;
                var sum = list.length;
                var tmp = list.slice(0);
                var lower = $(this).val().toLowerCase();
                while(i < sum) {
                    if(tmp[i].text().toLowerCase().indexOf(lower) == -1) {
                        tmp.splice(i, 1);
                        sum -= 1;
                    } else
                        i += 1;
                }
                args_func(tmp, args);
                func.apply(this, args);
            }
        });
    }

    function init_lander_option(lander) {
        path_tmp.lander = lander;
    }

    function init_offer_option(offer) {
        path_tmp.offer = offer;
    }

    function add_inner_2(inner_div_name, select_name, name) {
        var inner = '<select id="'+select_name+'" multiple="multiple" data-placeholder="Select '+name+'">';
        $("#"+inner_div_name).append(inner);
    }

    function add_inner_3(inner_div_name, area_name) {
        var inner = $('<textarea id="'+area_name+'" rows="8" cols="70" style="width:auto;overflow-x:scroll;white-space:nowrap"></textarea>');
        if(click_arg && click_arg.rules)
            inner.text(click_arg.rules);
        $("#"+inner_div_name).append(inner);
    }

    function add_inner_4(inner_div_name, input_name) {
        var inner = $('<input id="'+input_name+'" ></input>');
        if(click_arg && click_arg.rules)
            inner.val(click_arg.rules);
        $("#"+inner_div_name).append(inner);
    }

    function on_textarea_change(content_div_name, textarea_name, node, id) {
        $("#"+textarea_name).bind("input propertychange", function() {
             $.extend(node.value[content_div_name], get_type_3_val_cb(textarea_name, id));
        });
    }

    function on_input_change(content_div_name, input_name, node, id) {
        $("#"+input_name).bind("input propertychange", function() {
             $.extend(node.value[content_div_name], get_type_4_val_cb(input_name, id));
        });
    }

    function get_treeview_data() {
        var p = JSON.parse(JSON.stringify(path_tmp));
        p.text = "Path1";
        var d = JSON.parse(JSON.stringify(default_swap));
        d.items = [p, add_path_tmp]
        return [flow_tmp, d, add_rule_tmp];
    }

    function add_treeview_rule(root) {
        var r = JSON.parse(JSON.stringify(rule_tmp));
        r.items = [path_tmp, add_path_tmp]
        root.append(r);
    }

    function add_treeview_path(parent, n) {
        var p = JSON.parse(JSON.stringify(path_tmp));
        p.text = p.text+n;
        p.n = n
        p.weight = 100;
        parent.append(p);
    }

    function copy_treeview_path(parent, n, node) {
        copynode = node.toJSON()
        copynode.id = undefined;
        copynode.index = n - 1
        copynode.n = n
        parent.append(copynode);
    }

    function add_pannel(parent_id, id) {
        var p = $("#"+parent_id);
        var c = p.children();
        if(c.length == 0)
            var css_cls = "pannel_first";
        else {
            var css_cls = "pannel_last";
        }
        var l = "<div id='"+id+"' class='"+css_cls+"'>";
        p.append(l);
    }

    function add_pannel_child(parent_id, name, options, node, is_weight) {
        var p = $("#"+parent_id);
        var s = '<div id="'+name+'_pannel" class="pannel-title"><span>'+name+'</span/></div>';
        var ul = '<div class="pannel-content">\
                    <ul id="ul_'+name+'" style="list-style-type:none;margin:0px;"></ul>\
                    <div class="clear"><button type=button class="btn pull-right" id="add_'+name+'">Add '+name+'</button></div>\
                  </div>';
        p.append(s);
        p.append(ul);
        $("#add_"+name).click(function() {
            add_li("ul_"+name, name, node, is_weight);
        })
        if(node.value) {
            for(var i in node.value) {
                if(i.indexOf(name) != 0) continue;
                $("#add_"+name).click();
            }
        }
    }

    function add_li(ul_name, name, node, is_weight) {
        var li_cls = "special_li";
        var len = $("#"+ul_name).children().length;
        if(len%2 == 1)
            li_cls = "normal_li";
        var li = $("<li class='"+li_cls+"'></li>");
        var container = $("<div class='row-fluid'></div>");
        var close_btn = $('<a href="#" class="pull-right icon-remove icon"/>');
        var select = $("<select class='span10 offer-pannel' id='slc_"+name+len+"'></select>");
        var weight = $("");
        container.append(select);
        if (is_weight) {
            if(!node.value[name+len])
                node.value[name+len] = {};
            if(!node.value[name+len].weight)
                node.value[name+len].weight = "0";
            weight = $("<input class='span3' style='margin-left:15px' type='text' value='"+node.value[name+len].weight+"'>")
            //container.append(weight);
        }
        container.append(close_btn);
        li.append(container);
        $("#"+ul_name).append(li);
        var v = -1;
        if(node.value && node.value[name+len]!=undefined && node.value[name+len].val)
            v = node.value[name+len].val;

        if(is_weight) {
            weight.blur(function() {
                if(!node.value[name+len]) node.value[name+len] = {};
                node.value[name+len].weight = weight.val();
            })
        }

        var slc = select.kendoDropDownList({
            change: function() {
                if(!node.value[name+len]) node.value[name+len] = {};
                node.value[name+len].val = this.value();
            },
            open: function(e) {
            },
            filter:"contains",
            dataSource: get_datasource(node[name]),
            dataTextField: "text",
            dataValueField: "value",
            optionLabel: ["select", name, "..."].join(" "),
        }).data("kendoDropDownList");

        if(node.value && node.value[name+len]!=undefined && node.value[name+len].val)
            slc.value(node.value[name+len].val)

        close_btn.click(function() {
            if(select.attr("disabled")) {
                slc.enable();
                weight.removeAttr("disabled");
                close_btn.removeClass("icon-repeat");
                close_btn.addClass("icon-remove");
                node.value[name+len] = {val:slc.value()};
                if(is_weight)
                    node.value[name+len].weight = weight.val();
            } else {
                if(node.value)
                    delete node.value[name+len];
                slc.enable(false);
                weight.attr("disabled", "disabled");
                close_btn.removeClass("icon-remove");
                close_btn.addClass("icon-repeat");
            }
        });
    }
    function get_datasource(options) {
        var data = [];
        for(var i = 0; i < options.length; i++)
            data.push({value:options[i][0], text:options[i][1]})
        return data;
    }

    function add_li_options(select_name, options, data) {
        for(var i = 0; i < options.length; i++) {
            var select_s = "";
            if(options[i][0] == data)
                select_s = " selected";
            $("#"+select_name).append("<option value="+options[i][0]+select_s+">"+options[i][1]+"</options>");
        }
    }

    function init_flow_body(node) {
        var body = "<label>Name</label><input id='flow_name' value='"+node.text+"'>";
        $("#flow-modal-body").append(body);
        $("#flow_name").bind("input propertychange", function() {
            node.set("text", $("#flow_name").val());
        });
    }

    function init_path_body(node, treeview) {
        var body = [
            "<div class='row-fluid'>",
            "<div class='span3'><label for='path_name'>Name</label><input class='span12' id='path_name' value='", node.text, "'></div>",
            "<div class='span3'><label for='weight'>Weight</label><input id='weight' value='", node.weight, "' class='span12'></div>",
            "<div class='span3'><label for='direct_linking'>DireckLink</label><select id='direct_linking' class='span12'></select></div>",
            "<div class='span3 clone-btn'><button type='button' id='clone_path' style='position:absolute;bottom:0px;' class='btn' >clone</button></div>",
            "</div>"
        ];
        body.push("<div id='swap_pannel' class='row-fluid pannel_container'></div>");
        body = body.join("");
        $("#flow-modal-body").append(body);

        add_pannel("swap_pannel", "lander");
        add_pannel("swap_pannel", "offer");
        add_pannel_child("lander", "lander", node.lander, node, true);
        add_pannel_child("offer", "offer", node.offer, node);
        $("#path_name").bind("input propertychange", function() {
            node.set("text", $("#path_name").val());
        });

        $("#clone_path").click(function() {
            var parent_node = node.parentNode();
            var l = parent_node.children.data().length;

            last_node = treeview.findByUid(parent_node.children.data().at(l-1).uid)[0];
            last_node_data = treeview.dataItem(last_node)


            treeview.remove(last_node);
            copy_treeview_path(parent_node, l-1, node);
            parent_node.append(last_node_data);

            var last_node = parent_node.items[parent_node.items.length - 2]
            var f = treeview.findByUid(last_node.uid);
            treeview.select(f);
            treeview.trigger("select", {node: f});
        });

        $("#weight").bind("input propertychange", function() {
            node.set("weight", $("#weight").val());
        });

        function onDirectLinkSelect(e)
        {
            var dataItem = this.dataItem(e.item);
            node.set("direct_linking", dataItem.val);
        }

        $("#direct_linking").kendoDropDownList({
                dataTextField:"text",
                dataValueField:"val",
                dataSource:[
                    {'val':0, 'text':"NO"},
                    {'val':1, 'text':"YES"},
                ],
                select:onDirectLinkSelect,
            })
        $("#direct_linking").data("kendoDropDownList").value(node.direct_linking);
    }

    function init_rule_body(node, conf, rule_first_category, option_conf, options) {
        var name = "<label>Name</label><input id='rule_name' value='"+node.text+"'>";
        var body = $("#flow-modal-body");
        body.append(name);
        $("#rule_name").bind("input propertychange", function() {
            node.set("text", $("#rule_name").val());
        });
        var add_rule_div = ' <div class="dropdown">\
            <button id="rule_dropdown" class="btn dropdown-toggle" id="dLabel" role="button" data-toggle="dropdown" data-target="#">\
                <div style="min-width:100px" class="inline">Add condition<b class="caret inline"></b></div>\
            </button>\
            <ul class="dropdown-menu" role="menu" aria-labelledby="dLabel">';
        var l = [add_rule_div];
        for(var i in conf) {
            l.push('<li class="option" id="rule_dropdown_');
            l.push(conf[i].name.split(" ").join("-"));
            l.push('" ><span>');
            l.push(conf[i].name);
            l.push('</span></li>');
        }
        l.push('</ul></div><div class="accordion admin-accordion" id="rule_container"></div>');
        var b = l.join("");
        body.append(b);
        var count = {};
        for(var i in conf) {
            var type = conf[i].type,
                title = conf[i].name,
                name = title.split(" ").join("-"),
                id = conf[i].id;
            bind_dropdown_click(id, title, name, type, count, option_conf, options, i, rule_first_category, node);
        }
        if(!isJsonEmpty(node.value)) {
            var data = [];
            for(var i in node.value) {
                if(!in_rule_type(i)) continue;
                data.push([i.split("_"), $.extend(true, {}, node.value[i])]);
            }
            data.sort(function(a, b) {return a[0][1]-b[0][1];});
            data = data.map(function(a) {return [a[0][0], a[1]]});
            for (var i in data) {
                var type_name = data[i][0].split(" ").join("-");
                click_arg = data[i][1];
                $("#rule_dropdown_"+type_name).click();
            }
            click_arg = null;
        }
    }
    function in_rule_type(name) {
        for(var i in rule_type_name_container) {
            if(name.indexOf(rule_type_name_container[i]) != -1) return true;
        }
        return false;
    }


    function bind_dropdown_click(id, title, name, type, count, conf, options, indx, rule_first_category, node) {
        $("#rule_dropdown_"+name).click(function(e) {
               $("#rule_dropdown").dropdown('toggle');
               $(this).toggle();
               var n = $("#rule_container").children().length;
               var div_name = ["collapse", name, n].join("_");
               var close_btn_name = ["close", name, n].join("_");
               var content_div_name = [name, n].join("_");
               var inner_div_name = ["inner", name, n].join("_");
               add_collapse("rule_container", div_name, content_div_name, close_btn_name, inner_div_name, name, title, node);
               if(type == 1) {
                   if(!sec_cate_conf[name]) {
                       sec_cate_conf[name] = {};
                   }
                   top_cate[content_div_name] = parse_li(rule_first_category[id]);
                   sec_cate[content_div_name] = {};
                   add_inner_1(content_div_name, inner_div_name);

                   var ul_1 = $("#ul_1_"+content_div_name);
                   var ul_2 = $("#ul_2_"+content_div_name);
                   var ul_3 = $("#ul_3_"+content_div_name);
                   init_top_li(content_div_name, name, ul_1, ul_2, ul_3, node, id);
               } else if (type == 2) {
                   var select_name = "select_" + content_div_name;
                   add_inner_2(inner_div_name, select_name, name);
                   init_option(id, select_name, content_div_name, name, conf, options, indx, rule_first_category, node);
                   $("#"+select_name).kendoMultiSelect({
                        autoClose: false,
                        change:function () {
                            if(this.value().indexOf("1") != -1)
                               this.value("1");
                            $.extend(node.value[content_div_name], get_type_2_val_cb(select_name, id));
                        }
                    }).data("kendoMultiSelect");
               } else if (type == 3) {
                   var textarea_name = "area_" +content_div_name;
                   add_inner_3(inner_div_name, textarea_name, node);
                   on_textarea_change(content_div_name, textarea_name, node, id);
               } else if (type == 4) {
                   var input_name = "input_" + content_div_name;
                   add_inner_4(inner_div_name, input_name, node);
                   on_input_change(content_div_name, input_name, node, id);
               } else if (type == 5) {
                   var select_name = "select_" + content_div_name;
                   add_inner_2(inner_div_name, select_name, name);
                   init_option(id, select_name, content_div_name, name, conf, options, indx, rule_first_category, node);
                   $("#"+select_name).kendoMultiSelect({
                        autoClose: false,
                        change:function () {
                            $.extend(node.value[content_div_name], get_type_2_val_cb(select_name, id));
                        }
                    }).data("kendoMultiSelect")
               } else {
               }
               count[name] += 1;
        })
    }


    function get_type_1_val_cb(ul_3, id) {
        var ret = [];
        if (ul_3.find("li").length) {
            ul_3.find("li").each(function () {
                ret.push($(this).val());
            });
            return {rules:ret, type:id};
        }
        return {rules:[], type:id};
    }

    function get_type_2_val_cb(select_name, type_id) {
        var val = $("#"+select_name).val();
        if(val) {
            var ret = val.map(function(v, k) {return parseInt(v);});
            return {rules:ret, type:type_id};
        }
        return {rules:[]};
    }

    function get_type_3_val_cb(area_name, type_id) {
        var val = $("#"+area_name).val();
        if(val) {
            return {rules:val, type:type_id};
        }
        return {rules:"", type:type_id};
    }

    function get_type_4_val_cb(input_name, type_id) {
        return get_type_3_val_cb(input_name, type_id);
    }

    function parse_li(list) {
        return list.map(function(v, k) {
           var top_cate = "";
           top_cate=" sec_cate="+v.sec;
           var li = $("<li value="+v.id+top_cate+" >"+v.name+"</li>");
           return li;
       })
    }

    function init_top_li(name, type_name, ul1, ul2, ul3, node, id) {
        add_top_li(name, type_name, ul1, top_cate[name], ul2, ul3, node, id);
        bind_search(
            $("#search_1_"+name),
            ul1, top_cate[name],
            add_top_li,
            [name, type_name, ul1, top_cate[name], ul2, ul3, node, id],
            function(list, args) { args[3] = list; }
        );
    }

    function add_top_li(name, type_name, ul1, li_list, ul2, ul3, node, id) {
        for(var i in li_list) {
            var li = li_list[i];
            click_top_li(li_list[i], name, type_name, ul2, ul3, node, id);
            li.appendTo(ul1);
        }
    }

    function click_top_li(li, name, type_name, ul2, ul3, node, id) {
        li.click(function() {
            var from_top = false;
            if(!$(this).attr("selected")) {
                $(this).attr("selected", "selected");
                $(this).addClass("selected-border-gray");
                from_top = true;
            }
            init_sec_li(name, type_name, parseInt($(this).val()), ul2, ul3, from_top, node, id)
        })
        if(click_arg && click_arg.rules && click_arg.rules.length!=0)
            init_sec_li(name, type_name, parseInt(li.val()), ul2, ul3, false, node, id)
    }

    function init_sec_li(name, type_name, id, ul, ul3, from_top, node, type_id) {
        ul.empty();
        if (!sec_cate[name][id]) {
            if (!sec_cate_conf[type_name][id]) {
                get_sec_cate_conf(type_name, id);
            }
            var list = parse_li(sec_cate_conf[type_name][id]);
            sec_cate[name][id] = list;
        }
        add_sec_li(name, type_name, ul, sec_cate[name][id], ul3, from_top, node, type_id);
        bind_search(
            $("#search_2_"+name),
            ul,
            sec_cate[name][id],
            add_sec_li,
            [name, type_name, ul, sec_cate[name][id], ul3, from_top, node, type_id],
            function(list, args) {args[3] = list;}
        );
    }

    function set_sec_cate_url(url) {
        sec_cate_url = url;
    }

    function get_sec_cate_conf(type_name, id){
        $.ajax({
            async:false,
            url:sec_cate_url,
            type:"GET",
            data:{id:id},
            success: function(data) {
                sec_cate_conf[type_name][id] = JSON.parse(data);
            }
        })
    }

    function add_sec_li(name, type_name, ul, li_list, ul3, from_top, node, id) {
        var has_selected = false;
        for(var i in li_list) {
            var li = li_list[i];
            if(li.attr("selected"))
                has_selected = true;
            li.appendTo(ul);
            click_sec_li(li, name, ul3, node, id);
        }
        var val_list = click_arg? click_arg.rules:[];
        var tmp = val_list.slice(0);

        if(!has_selected && !val_list.length) {
            for(var i in li_list) {
                li_list[i].attr("selected", "selected");
                li_list[i].addClass("selected-border-gray");
                add_display_ul(ul3, li_list[i], name, node, id);
            }
        }
        else if(val_list.length){
            for(var n in li_list) {
                for(var j = 0; j < val_list.length; j++) {
                    if(li_list[n].val() == val_list[j]) {
                        li_list[n].attr("selected", "selected");
                        li_list[n].addClass("selected-border-gray");
                        add_display_ul(ul3, li_list[n], name, node, id, true);

                        for(var n in top_cate[name]) {
                            if(top_cate[name][n].val() == parseInt(li_list[i].attr("sec_cate"))) {
                                top_cate[name][n].attr("selected", "selected");
                                top_cate[name][n].addClass("selected-border-gray");
                                break;
                            }
                        }
                        array_remove(tmp, val_list[j]);
                        break;
                    }
                }
                if(!tmp.length) break
            }
            click_arg.rules = tmp;
        }
    }

    function array_remove(list, val) {
        var index = list.indexOf(val);
        if (index > -1) {
            list.splice(index, 1);
        }
    }

    function click_sec_li(li, name, ul3, node, id){
        li.click(function() {
            if(!$(this).attr("selected")) {
                $(this).attr("selected", "selected")
                $(this).addClass("selected-border-gray");
                active_top_selected(name, parseInt($(this).attr("sec_cate")));
                add_display_ul(ul3, $(this), name, node, id);
            } else {
                cancel_sec_selected($(this), ul3, name, node, id);
            }
        })
    }

    function active_top_selected(name, val) {
        var is_empty = true;
        var l = sec_cate[name][val];
        for (var i in l) {
            if(l[i].attr('selected')){
                is_empty = false;
                break;
            }
         }
        if(!is_empty) {
            for(var i in top_cate[name]) {
                if(top_cate[name][i].val() == val) {
                    top_cate[name][i].attr("selected", "selected");
                    top_cate[name][i].addClass("selected-border-gray");
                }
            }
        }
    }

    function add_display_ul(ul3, sec_li, name, node, id, only_dispaly) {
        var btn = $('<button type="button" class="close">×</button>');
        var li = $("<li value='"+sec_li.val()+"'>"+sec_li.text()+"</li>");
        btn.appendTo(li);
        btn.click(function() {
            cancel_sec_selected(sec_li, ul3, name, node, id);
        });
        li.appendTo(ul3);
        if(!only_dispaly)
            $.extend(node.value[name], get_type_1_val_cb(ul3, id));
    }

    function cancel_sec_selected(li, ul3, name, node, id) {
        li.removeAttr("selected");
        li.removeClass("selected-border-gray");
        remove_display_ul(ul3, li.val());
        cancel_top_selected(name, parseInt(li.attr("sec_cate")));
        $.extend(node.value[name], get_type_1_val_cb(ul3, id));
    }

    function remove_display_ul(ul3, id) {
        ul3.find("li[value='"+id+"']").remove();
    }

    function cancel_top_selected(name, val) {
        var is_empty = true;
        var l = sec_cate[name][val];
        for (var i in l) {
            if(l[i].attr('selected')){
                is_empty = false;
                break;
            }
         }
        if(is_empty) {
            for(var i in top_cate[name]) {
                if(top_cate[name][i].val() == val) {
                    top_cate[name][i].removeAttr("selected");
                    top_cate[name][i].removeClass("selected-border-gray");
                }
            }
        }
    }

    function init_option(id, select_name, name, type_name, conf, options, indx, rule_first_category, node) {
        if (!sec_cate_conf[type_name]) {
            sec_cate_conf[type_name] = {};
            for (var i in rule_first_category[id]) {
                get_sec_cate_conf(type_name, rule_first_category[id][i].id);
            }
            var tmp = [];
            for (var i in sec_cate_conf[type_name]) {
                tmp = tmp.concat(sec_cate_conf[type_name][i]);
                sec_cate_conf[type_name] = tmp;
            }
        }

        for(var i in sec_cate_conf[type_name]) {
            var option = sec_cate_conf[type_name][i];
            var selected = " "
            if(node.value[name] && node.value[name].rules && node.value[name].rules.indexOf(option.id) != -1) {
                selected = " selected";
            }
            var option_obj = $("<option value='"+ option.id+"' "+selected+">"+option.name+"</option>");
            option_obj.appendTo($("#"+select_name));
        }
    }

    function get_treeview_value(treeview) {
        var nodes = treeview.root[0].children;
        var rules = [];
        var flow = {};
        var default_swap;
        for(var i = 0;i < nodes.length; i++) {
            var node = treeview.dataItem(nodes[i]);
            switch(node.type) {
                case "flow":
                    flow.name = node.text;
                    flow.id = node.id;
                    break;
                case "normal": 
                    var ret = get_path_value(node.items);
                    if(typeof ret == "string") return {error:ret}
                    flow.default_swap = {id:node.id, paths:ret};
                    break;
                case "rule":
                    var ret_paths = get_path_value(node.items);
                    if(typeof ret_paths == "string") return {error:ret_paths};
                    var ret_rules = get_rule_value(node.value);
                    if (typeof ret_rules == "string") return {error:ret_rules};
                    var rule = {id:node.id, paths:ret_paths, condition: ret_rules, name: node.text};
                    rules.push(rule);
                    break;
            }
        }
        flow.rules = rules;
        return JSON.stringify(flow);
    }

    function is_unique(array) {
        var t = {};
        for(var i in array) {
            if (t[array[i][1].val]) return false;
            else t[array[i][1].val] = 1;
        }
        return true;
    }

    function check_weight(w) {
        var reg = new RegExp("^[0-9]*$");
        return reg.test(w);
    }

    function get_path_value(nodes) {
        var paths = []
        for(var j = 0; j < nodes.length; j++) {
            if(nodes[j].type == "path") {
                var lander = [],
                    offer = [];
                for(var i in nodes[j].value) {
                    if(i.indexOf("lander") == 0) {
                        if(!nodes[j].value[i].val || $.trim(nodes[j].value[i].val).length == 0)
                            return "lander couldn't be empty";
                        lander.push([i.slice(6), {weight:parseInt(nodes[j].value[i].weight), val:parseInt(nodes[j].value[i].val)}]);
                    } else if(i.indexOf("offer") == 0) {
                        if(!nodes[j].value[i].val || $.trim(nodes[j].value[i].val).length == 0)
                            return "offer couldn't be empty";
                        offer.push([i.slice(5), {val:parseInt(nodes[j].value[i].val)}]);
                    }
                }
                if (!nodes[j].weight)
                    return "path weight couldn't be empty";
                if (!offer.length || !lander.length )
                    return "offer and lander couldn't be empty";
                if (!is_unique(lander))
                    return "offer and lander couldn't be duplicated";
                var f1 = function(a, b) {return a[0] - b[0]};
                lander.sort(f1);
                offer.sort(f1);
                var m = function(a) {return a[1];};
                lander = lander.map(m);
                offer = offer.map(m);

                if(!check_weight(nodes[j].weight)) return "path weight must be int and bingger than 0";
                paths.push({id:nodes[j].id, lander:lander, offer:offer, name:nodes[j].text, weight:parseInt(nodes[j].weight), direct_linking:nodes[j].direct_linking});
            }
        }
        return paths;
    }

    function get_rule_value(rules) {
        var ret = [];
        for(var i in rules) {
            if(!in_rule_type(i)) continue
            if(!rules[i].rules || rules[i].rules == []) return "rules couldn't be empty";
            ret.push([i.split("_")[1], rules[i]]);
        }
        ret.sort(function(a, b) {return a[0] - b[0];});
        ret = ret.map(function(a) {return a[1]});
        return ret
    }


    function init_treeview_data(flow) {
        var f = JSON.parse(JSON.stringify(flow_tmp));
        f.text = flow.name;
        f.id = flow.id;
        var default_swap = init_treeview_default_path(flow.default_swap);
        ret = [f, default_swap];
        for(var i in flow.rules) {
            var rule = init_treeview_rule(flow.rules[i]);
            ret.push(rule);
        }
        ret.push(add_rule_tmp);
        return ret;
    }

    function init_treeview_default_path(swap) {
        var d = JSON.parse(JSON.stringify(default_swap));
        d.id = swap.id
        for(var i in swap.paths) {
            var p = init_treeview_path(swap.paths[i]);
            d.items.push(p);
        }
        d.items.push(add_path_tmp);
        return d;
    }

    function init_treeview_path(path) {
        var p = JSON.parse(JSON.stringify(path_tmp));
        p.value = {};
        p.id = path.id;
        p.text = path.name;
        p.weight = path.weight
        p.direct_linking = path.direct_linking
        for(var j in path.lander) {
            //p.value['lander'+j] = {val:path.lander[j].val, weight:path.lander[j].weight};
            p.value['lander'+j] = {val:path.lander[j].val, weight:0};
        }
        for(var j in path.offer) {
            p.value['offer'+j] = {val:path.offer[j].val};
        }
        return p;
    }

    function init_treeview_rule(rule) {
        var r = JSON.parse(JSON.stringify(rule_tmp));
        for(var i in rule.paths) {
            var p = init_treeview_path(rule.paths[i]);
            r.items.push(p);
        }
        r.items.push(add_path_tmp);
        r.id = rule.id;
        r.text = rule.name;
        var n = 0;
        r.value = {};
        for(var i in rule.condition) {
            r.value[rule.condition[i].rule_type_name + "_" + n] = rule.condition[i];
            delete rule.condition[i].rule_type_name
            n++;
        }
        return r
    }

function initPjaxTag(a, container) {
    ajaxObj = new myAjax(container);
    a.each(function(_, v) {
        $(v).click(function(e) {
            if(!e.metaKey) {
                var url = $(this).attr("href");
                ajaxObj.ajax(url);
                return false;
            }
        });
    })
}

function initPjaxForm(a, container) {
    ajaxObj = new myAjax(container);
    a.each(function(_, v) {
        $(v).submit(function() {
            var url = $(this).attr("action")
            ajaxObj.form_ajax(url, $(v).serialize());
            return false;
        });
    })
}


function myAjax(select) {
    this.select = select;
}


myAjax.prototype.form_ajax = function(url, post_params) {
    that = this;
    var arg = {
        url:url,
        type:"POST",
        data:post_params,
        beforeSend: function(request) {
            request.setRequestHeader("Transform-Type", "pjax");
        },
        success:function(data) {
            if(typeof data == "object") {
                if(data.error) {
                    location.href = "/";
                    return;
                } else {
                    url = data.url
                    data = data.html
                }
            }
            var history_html = $(that.select).html();
            $(that.select).html(data);
            $(that.select).animate({scrollTop:0}, 1200);
            history.pushState({html:data}, document.title, url);
        }
    };
    $.ajax(arg);
}

myAjax.prototype.ajax = function(url, get_params, post_params){
    that = this;
    get_params = get_params ? get_params:{};
    post_params = post_params ? post_params:{};
    url_params = [];
    for(var k in get_params) {
        url_params.push(k + "=" + get_params[k]);
    }
    url_params = url_params.join("&");
    url = url_params?url + "?" + url_params:url;
    var arg = {
        url:url,
        type:"GET",
        beforeSend: function(request) {
            request.setRequestHeader("Transform-Type", "pjax");
        },
        success:function(data) {
            if(typeof data == "object") {
                if(data.error) {
                    location.href = "/";
                    return;
                } else {
                    url = data.url
                    data = data.html
                }
            }
            var history_html = $(that.select).html();
            $(that.select).html(data);
            $(that.select).animate({scrollTop:0}, 1200);
            history.pushState({html:data}, document.title, url);
        }
    };
    if(post_params.length) {
        arg.type = "POST";
        arg.data = post_params;
    }
    $.ajax(arg);
}



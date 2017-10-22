webpackJsonp([0],{108:function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.Result=void 0;var n=a(68),r=function(e){return e&&e.__esModule?e:{default:e}}(n),s={HEADER:(0,r.default)("cpp-header"),NAMESPACE:(0,r.default)("cpp-namespace"),CLASS:(0,r.default)("cpp-class"),FUNCTION:(0,r.default)("cpp-function"),MEM_FUN:(0,r.default)("cpp-mem_fun"),ENUM:(0,r.default)("cpp-enum"),VARIABLE:(0,r.default)("cpp-variable"),TYPE_ALIAS:(0,r.default)("cpp-type-alias"),MACRO:(0,r.default)("cpp-macro"),ARTICLE:(0,r.default)("article"),META:(0,r.default)("meta"),GOOGLE_FALLBACK:(0,r.default)("google-fallback")};t.Result=s},110:function(e,t,a){(function(t){e.exports=t.CRSearch=a(111)}).call(t,a(11))},111:function(e,t,a){"use strict";function n(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0}),t.Database=void 0;var r=a(112),s=n(r),i=a(23),l=n(i),u=a(42),d=n(u),o=a(17),c=n(o),h=a(18),f=n(h),p=(a(26),a(70)),_=a(118),v=function(){function e(t){(0,c.default)(this,e),this.name=t.database_name,this.base_url=new URL(t.base_url),this.namespaces=[],this.ids=[];var a=!0,n=!1,r=void 0;try{for(var s,i=(0,l.default)(t.ids.entries());!(a=(s=i.next()).done);a=!0){var u=s.value,o=(0,d.default)(u,2),h=o[0],f=o[1];this.ids.push(new p.IndexID(h,f))}}catch(e){n=!0,r=e}finally{try{!a&&i.return&&i.return()}finally{if(n)throw r}}var v=!0,y=!1,m=void 0;try{for(var g,k=(0,l.default)(t.namespaces.entries());!(v=(g=k.next()).done);v=!0){var R=g.value,w=(0,d.default)(R,2),S=w[0],b=w[1];this.namespaces.push(new _.Namespace(S,b,this.ids))}}catch(e){y=!0,m=e}finally{try{!v&&k.return&&k.return()}finally{if(y)throw m}}}return(0,f.default)(e,[{key:"query",value:function(e,t,a){var n=[],r=!0,i=!1,u=void 0;try{for(var d,o=(0,l.default)(this.namespaces);!(r=(d=o.next()).done);r=!0){var c=d.value,h=c.query(e,t,a,this.make_url.bind(this));if(0!=h.targets.length&&(t=h.found_count,n.push.apply(n,(0,s.default)(h.targets)),t>a))return{targets:n,found_count:t}}}catch(e){i=!0,u=e}finally{try{!r&&o.return&&o.return()}finally{if(i)throw u}}return{targets:n,found_count:t}}},{key:"make_url",value:function(e){return new URL("/"+e+".html",this.base_url)}}]),e}();t.Database=v},117:function(e,t,a){"use strict";(function(e){function n(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0}),t.IndexID=void 0;var r=a(43),s=n(r),i=a(68),l=n(i),u=a(17),d=n(u),o=a(18),c=n(o),h=a(26),f=function(){function t(e,a){var n=this;(0,d.default)(this,t),this.s_key=e;var r=a.key;switch(this.type=["header","namespace","class","function","mem_fun","enum","variable","type-alias","macro"].includes(a.type)?(0,l.default)("cpp-"+a.type):(0,l.default)(a.type),this.type){case h.Result.CLASS:case h.Result.FUNCTION:case h.Result.MEM_FUN:case h.Result.ENUM:case h.Result.VARIABLE:case h.Result.TYPE_ALIAS:var s=["std"];a.cpp_namespace&&(s=a.cpp_namespace),r=s.concat(r)}this.key=r.map(function(e){return{name:e.normalize("NFKC")}}),t.VERBATIM_TRS.forEach(function(e,t){e.only&&e.only!==n.type||n.key[n.key.length-1].name.includes(t)&&(n.key[n.key.length-1]={name:n.key[n.key.length-1].name.replace(t,""+e.to),classes:["special"]},e.type&&(n.type=e.type,n.type===h.Result.CLASS&&"std"!==n.key[0]&&n.key.unshift({name:"std"})))})}return(0,c.default)(t,[{key:"equals",value:function(e){return this.s_key===e.s_key&&this.ns_id===e.ns_id}}]),(0,c.default)(t,[{key:"join",value:function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:this.join_hint();return""+(e.wrap.left||"")+this.key.map(function(e){return e.name}).join(e.delim.text)+(e.wrap.right||"")}},{key:"join_html",value:function(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:this.join_hint(),a=e('<div class="key-container delim-'+t.delim.name+'" />');if(t.wrap.left){var n=e('<span class="wrap" />');n.text(t.wrap.left),n.appendTo(a)}var r=e('<div class="keys" />');if(r.appendTo(a),this.key.forEach(function(t){var a=e('<span class="key" />');t.classes&&t.classes.forEach(function(e){return a.addClass(e)}),a.text(t.name),a.appendTo(r)}),t.wrap.right){var s=e('<span class="wrap" />');s.text(t.wrap.right),s.appendTo(a)}return a}},{key:"join_hint",value:function(){var e={delim:{name:"none",text:""},wrap:{}};switch(this.type){case h.Result.HEADER:e={wrap:{left:"<",right:">"},delim:{name:"slash",text:"/"}};break;case h.Result.NAMESPACE:case h.Result.CLASS:case h.Result.FUNCTION:case h.Result.MEM_FUN:case h.Result.ENUM:case h.Result.VARIABLE:case h.Result.TYPE_ALIAS:e.delim={name:"ns",text:"::"}}return e}}]),t}();f.VERBATIM_TRS=new s.default([["コンストラクタ",{to:"(constructor)",only:h.Result.MEM_FUN}],["デストラクタ",{to:"(destructor)",only:h.Result.MEM_FUN}],["推論補助",{to:"(deduction guide)",type:h.Result.CLASS}],["非メンバ関数",{to:"non-member function",type:h.Result.FUNCTION}],["単項",{to:"unary"}]]),t.IndexID=f}).call(t,a(45))},118:function(e,t,a){(function(t){e.exports=t.CRSearch=a(119)}).call(t,a(11))},119:function(e,t,a){"use strict";function n(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0}),t.Namespace=void 0;var r=a(69),s=n(r),i=a(42),l=n(i),u=a(120),d=n(u),o=a(23),c=n(o),h=a(43),f=n(h),p=a(17),_=n(p),v=a(18),y=n(v),m=a(126),g=function(){function e(t,a,n){(0,_.default)(this,e),this.ns_id=t,this.indexes=new f.default,this.namespace=a.namespace,a.path_prefixes?this.path_prefixes=a.path_prefixes.join("/"):this.path_prefixes=this.namespace.join("/");var r=!0,s=!1,i=void 0;try{for(var l,u=(0,c.default)(a.indexes);!(r=(l=u.next()).done);r=!0){var d=l.value,o=new m.Index(n[d.id],d);this.indexes.set(o.id_cache,o)}}catch(e){s=!0,i=e}finally{try{!r&&u.return&&u.return()}finally{if(s)throw i}}}return(0,y.default)(e,[{key:"query",value:function(e,t,a,n){var r=[],i=e.normalize("NFKC").split(/\s+/).filter(Boolean).reduce(function(e,t){return"-"===t[0]?e.not.add(t.substring(1)):e.and.add(t),e},{and:new d.default,not:new d.default});i.not.delete("");var u=!0,o=!1,h=void 0;try{for(var f,p=(0,c.default)(this.indexes);!(u=(f=p.next()).done);u=!0){var _=f.value,v=(0,l.default)(_,2),y=(v[0],v[1]);if((0,s.default)(i.and).every(function(e,t){return m.Index.ambgMatch(e,t)}.bind(null,y))&&!(0,s.default)(i.not).some(function(e,t){return m.Index.ambgMatch(e,t)}.bind(null,y))){if(++t>a)return{targets:r,found_count:t};r.push({path:n(this.make_path(y.page_id)),index:y})}}}catch(e){o=!0,h=e}finally{try{!u&&p.return&&p.return()}finally{if(o)throw h}}return{targets:r,found_count:t}}},{key:"make_path",value:function(e){return this.path_prefixes+"/"+e.join("/")}}]),e}();t.Namespace=g},126:function(e,t,a){(function(t){e.exports=t.CRSearch=a(127)}).call(t,a(11))},127:function(e,t,a){"use strict";function n(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0}),t.Index=void 0;var r=a(17),s=n(r),i=a(18),l=n(i),u=a(26),d=(a(70),function(){function e(t,a){(0,s.default)(this,e),this.id=t,this.page_id=a.page_id,this.id_cache=this.join()}return(0,l.default)(e,[{key:"type",value:function(){return this.id.type}},{key:"join_html",value:function(){return this.id.join_html()}},{key:"join",value:function(){return this.id.join()}}],[{key:"ambgMatch",value:function(e,t){return[u.Result.ARTICLE,u.Result.META].includes(e.id.type)?e.id_cache.toLowerCase().includes(t.toLowerCase()):e.id_cache.includes(t)}}]),e}());t.Index=d},26:function(e,t,a){(function(t){e.exports=t.CRSearch=a(108)}).call(t,a(11))},70:function(e,t,a){(function(t){e.exports=t.CRSearch=a(117)}).call(t,a(11))},71:function(e,t,a){(function(t){e.exports=t.CRSearch=a(72)}).call(t,a(11))},72:function(e,t,a){"use strict";(function(n){function r(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0});var s=a(73),i=r(s),l=a(23),u=r(l),d=a(42),o=r(d),c=a(43),h=r(c),f=a(17),p=r(f),_=a(18),v=r(_),y=a(107),m=r(y),g=a(26),k=a(110),R=function(){function e(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:e.OPTS_DEFAULT;(0,p.default)(this,e),this.opts=t,this.loaded=!1,this.db=new h.default,this.last_id=0,this.last_input={},this.search_timer={},m.default.bind("/",function(){return this.select_default_input()}.bind(this)),m.default.bind("esc",function(){return this.hide_all_result()}.bind(this)),this.dp("initialized.")}return(0,v.default)(e,[{key:"load",value:function(){var e=this,t=1,a=!0,r=!1,s=void 0;try{for(var i,l=(0,u.default)(this.db);!(a=(i=l.next()).done);a=!0){var d=i.value,c=(0,o.default)(d,2),h=c[0];c[1];!function(a,r){"/"==a.pathname&&(a.pathname="/crsearch.json"),e.dp("fetching database ("+t+"/"+e.db.size+"):",a),n.ajax({url:a,success:function(e){this.dp("fetched."),this.parse(a,e)}.bind(e),fail:function(){this.dp("fetch failed.")}.bind(e)}),++t}(h)}}catch(e){r=!0,s=e}finally{try{!a&&l.return&&l.return()}finally{if(r)throw s}}}},{key:"parse",value:function(e,t){this.dp("parsing...",t),this.db.set(e,new k.Database(t)),this.defaultUrl||(this.defaultUrl=new URL(this.db.get(e).base_url).hostname),this.updateSearchButton(""),this.dp("parsed.",this.db.get(e))}},{key:"database",value:function(e){try{var t=new URL(e);this.db.set(t.toString(),null)}catch(t){var a=document.createElement("a");a.href=e,"/"==a.pathname&&(a.pathname="/crsearch.json");var n=new URL(a.toString());this.db.set(n.toString(),null)}}},{key:"do_search",value:function(e){clearTimeout(this.search_timer[e.data.id]),this.search_timer[e.data.id]=setTimeout(function(e){this.do_search_impl(e)}.bind(this,e),20)}},{key:"do_search_impl",value:function(t){var a=this.last_input[t.data.id];this.dp("[query]",a);var r=this.clear_results_for(t.target),s={},i=new h.default,l=!0,d=!1,c=void 0;try{for(var f,p=(0,u.default)(this.db);!(l=(f=p.next()).done);l=!0){var _=f.value,v=(0,o.default)(_,2),y=(v[0],v[1]),m=y.query(a,0,e.MAX_RESULT);if(s[y.name]={url:y.base_url},i.set(y.name,m.targets),0!=i.get(y.name).length){m.found_count>e.MAX_RESULT?s[y.name].html=n('<div class="message">Showing first<span class="match-count">'+e.MAX_RESULT+"</span>matches</div>"):s[y.name].html=n('<div class="message">Showing<span class="match-count">all</span>matches</div>')}else s[y.name].html=n('<div class="message">No matches for <span class="query">'+a+"</span></div>")}}catch(e){d=!0,c=e}finally{try{!l&&p.return&&p.return()}finally{if(d)throw c}}var k=!0,R=!1,w=void 0;try{for(var S,b=(0,u.default)(i);!(k=(S=b.next()).done);k=!0){var E=S.value,A=(0,o.default)(E,2),L=A[0],T=A[1];r.append(this.make_result_header(L,s[L]));var x=!0,C=!1,M=void 0;try{for(var U,P=(0,u.default)(T);!(x=(U=P.next()).done);x=!0){var O=U.value;r.append(this.make_result(O.index.type(),O.index,O.path))}}catch(e){C=!0,M=e}finally{try{!x&&P.return&&P.return()}finally{if(C)throw M}}}}catch(e){R=!0,w=e}finally{try{!k&&b.return&&b.return()}finally{if(R)throw w}}var I=!0,N=!1,j=void 0;try{for(var B,F=(0,u.default)(this.db);!(I=(B=F.next()).done);I=!0){var K=B.value,q=(0,o.default)(K,2),D=(q[0],q[1]);r.append(this.make_result(g.Result.GOOGLE_FALLBACK,a,{name:D.name,url:D.base_url.host}))}}catch(e){N=!0,j=e}finally{try{!I&&F.return&&F.return()}finally{if(N)throw j}}}},{key:"make_result_header",value:function(e,t){var a=n('<li class="result" />');if(a.addClass("cr-result-header"),t.html){var r=n('<div class="extra" />');t.klass&&r.addClass(t.klass),t.html.appendTo(r),r.appendTo(a)}var s=n('<a class="db-name" />');return s.attr("href",t.url),s.attr("target","_blank"),s.text(e),s.appendTo(a),a}},{key:"make_google_url",value:function(e,t){var a=this.opts.google_url;return a.searchParams.set("q",e+" site:"+t),a}},{key:"make_result",value:function(t,a){var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:void 0,s=e.RESULT_PROTO.clone();s.addClass((0,i.default)(t));var l=s.children("a"),u=n('<div class="content" />').appendTo(l);switch(t){case g.Result.GOOGLE_FALLBACK:l.attr("href",this.make_google_url(a,r.url)),l.attr("target","_blank"),n('<div class="query">'+a+"</div>").appendTo(u),n('<div class="fallback-site">'+r.url+"</div>").appendTo(u);break;default:l.attr("href",r),a.join_html().appendTo(u),this.opts.force_new_window&&l.attr("target","_blank")}return s}},{key:"updateSearchButton",value:function(e){this.searchButton.attr("href",this.make_google_url(e,this.defaultUrl))}},{key:"searchbox",value:function(t){this.searchButton=n("<a />"),this.searchButton.attr("target","_blank"),this.searchButton.addClass("search");var a=!0,r=!1,s=void 0;try{for(var i,l=(0,u.default)(this.opts.klass.search_button);!(a=(i=l.next()).done);a=!0){var d=i.value;this.searchButton.addClass(d)}}catch(e){r=!0,s=e}finally{try{!a&&l.return&&l.return()}finally{if(r)throw s}}this.loaded||(this.loaded=!0,this.load());var o=this.last_id++;this.dp("creating searchbox",o);var c=n(t);n.data(c,"crsearch-id",o),this.last_input[o]="";var h=n('<div class="control" />');h.appendTo(c);var f=n('<input type="text" class="input">');f.attr("autocomplete",!1),f.attr("placeholder",e.INPUT_PLACEHOLDER),f.appendTo(h),f.on("click",function(e){return this.show_result_wrapper_for(e.target),this.select_default_input()}.bind(this)),f.on("keyup",{id:o},function(e){this.show_result_wrapper_for(e.target);var t=n(e.target).val().replace(/\s+/g," ").trim();return this.last_input[e.data.id]!=t&&(this.last_input[e.data.id]=t,this.updateSearchButton(t),t.length>=2?(this.find_result_wrapper_for(e.target).removeClass("help"),this.msg_for(e.target),this.do_search(e)):0==t.length?(this.clear_results_for(e.target),this.msg_for(e.target),this.find_result_wrapper_for(e.target).addClass("help")):(this.clear_results_for(e.target),this.msg_for(e.target,0==t.length?"":"input >= 2 characters..."),this.find_result_wrapper_for(e.target).addClass("help"))),!1}.bind(this)),this.default_input=f,(0,m.default)(f.get(0)).bind("esc",function(e){return n(e.target).blur(),this.hide_all_result()}.bind(this));var p=n("<div />");p.addClass(e.RESULT_WRAPPER_KLASS),p.addClass("help"),p.appendTo(c);var _=n("<ul />");_.addClass(e.RESULTS_KLASS),_.appendTo(p),n(e.HELP).appendTo(p);var v=n('<div class="crsearch-info" />'),y=n("<a />");y.attr("href",e.HOMEPAGE),y.attr("target","_blank"),y.text("CRSearch v"+e.VERSION),y.appendTo(v),v.appendTo(p),f.on("focusin",function(){return this.show_result_wrapper_for(this)}.bind(this)),this.searchButton.appendTo(h)}},{key:"select_default_input",value:function(){return this.default_input.select(),!1}},{key:"find_cr_for",value:function(t){return n(t).closest("."+e.KLASS)}},{key:"find_result_wrapper_for",value:function(t){return this.find_cr_for(t).children("."+e.RESULT_WRAPPER_KLASS)}},{key:"find_results_for",value:function(t){return this.find_result_wrapper_for(t).children("."+e.RESULTS_KLASS)}},{key:"show_result_wrapper_for",value:function(e){return this.find_result_wrapper_for(e).addClass("visible"),!1}},{key:"msg_for",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"";return this.find_cr_for(e).find(".result-wrapper .help-content .message").text(t),!1}},{key:"hide_result_wrapper_for",value:function(e){return this.find_result_wrapper_for(e).removeClass("visible"),!1}},{key:"clear_results_for",value:function(e){var t=this.find_results_for(e);return t.empty(),t}},{key:"hide_all_result",value:function(){return n("."+e.KLASS+" ."+e.RESULT_WRAPPER_KLASS).removeClass("visible"),!1}},{key:"dp",value:function(){var e;(e=console).log.apply(e,["[CRSearch]"].concat(Array.prototype.slice.call(arguments)))}}]),e}();R.VERSION="1.0.0",R.HOMEPAGE="https://github.com/cpprefjp/crsearch",R.OPTS_DEFAULT={klass:{search_button:["fa","fa-fw","fa-search"]},google_url:new URL("https://www.google.co.jp/search"),force_new_window:!1},R.KLASS="crsearch",R.RESULT_WRAPPER_KLASS="result-wrapper",R.RESULTS_KLASS="results",R.INPUT_PLACEHOLDER='"std::...", "<header>", etc.',R.MAX_RESULT=5,R.RESULT_PROTO=n('<li class="result"><a href="#"></a></li>'),R.HELP='\n    <div class="help-content">\n      <div class="message"></div>\n      <ul class="examples">\n        <li>\n          <h3>Class / Function / Type</h3>\n          <div class="query">std::<span class="input"></span></div>\n        </li>\n        <li>\n          <h3>Header file</h3>\n          <div class="query">&lt;<span class="input"></span>&gt;</div>\n        </li>\n        <li>\n          <h3>Other / All</h3>\n          <div class="query"><span class="input"></span></div>\n        </li>\n      </ul>\n    </div>\n  ',t.default=R,e.exports=R}).call(t,a(45))}},[71]);
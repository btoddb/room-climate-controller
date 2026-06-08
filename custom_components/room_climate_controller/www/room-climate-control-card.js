function e(e,t,i,s){var o,r=arguments.length,n=r<3?t:null===s?s=Object.getOwnPropertyDescriptor(t,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)n=Reflect.decorate(e,t,i,s);else for(var a=e.length-1;a>=0;a--)(o=e[a])&&(n=(r<3?o(n):r>3?o(t,i,n):o(t,i))||n);return r>3&&n&&Object.defineProperty(t,i,n),n}"function"==typeof SuppressedError&&SuppressedError;
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const t=globalThis,i=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),o=new WeakMap;let r=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(i&&void 0===e){const i=void 0!==t&&1===t.length;i&&(e=o.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&o.set(t,e))}return e}toString(){return this.cssText}};const n=(e,...t)=>{const i=1===e.length?e[0]:t.reduce((t,i,s)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[s+1],e[0]);return new r(i,e,s)},a=i?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new r("string"==typeof e?e:e+"",void 0,s))(t)})(e):e,{is:l,defineProperty:c,getOwnPropertyDescriptor:d,getOwnPropertyNames:h,getOwnPropertySymbols:p,getPrototypeOf:u}=Object,f=globalThis,m=f.trustedTypes,_=m?m.emptyScript:"",g=f.reactiveElementPolyfillSupport,v=(e,t)=>e,y={toAttribute(e,t){switch(t){case Boolean:e=e?_:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},b=(e,t)=>!l(e,t),$={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:b};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */Symbol.metadata??=Symbol("metadata"),f.litPropertyMetadata??=new WeakMap;let x=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=$){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(e,i,t);void 0!==s&&c(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){const{get:s,set:o}=d(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:s,set(t){const r=s?.call(this);o?.call(this,t),this.requestUpdate(e,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??$}static _$Ei(){if(this.hasOwnProperty(v("elementProperties")))return;const e=u(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(v("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(v("properties"))){const e=this.properties,t=[...h(e),...p(e)];for(const i of t)this.createProperty(i,e[i])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const i=this._$Eu(e,t);void 0!==i&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(a(e))}else void 0!==e&&t.push(a(e));return t}static _$Eu(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{if(i)e.adoptedStyleSheets=s.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const i of s){const s=document.createElement("style"),o=t.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=i.cssText,e.appendChild(s)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(void 0!==s&&!0===i.reflect){const o=(void 0!==i.converter?.toAttribute?i.converter:y).toAttribute(t,i.type);this._$Em=e,null==o?this.removeAttribute(s):this.setAttribute(s,o),this._$Em=null}}_$AK(e,t){const i=this.constructor,s=i._$Eh.get(e);if(void 0!==s&&this._$Em!==s){const e=i.getPropertyOptions(s),o="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:y;this._$Em=s;const r=o.fromAttribute(t,e.type);this[s]=r??this._$Ej?.get(s)??r,this._$Em=null}}requestUpdate(e,t,i,s=!1,o){if(void 0!==e){const r=this.constructor;if(!1===s&&(o=this[e]),i??=r.getPropertyOptions(e),!((i.hasChanged??b)(o,t)||i.useDefault&&i.reflect&&o===this._$Ej?.get(e)&&!this.hasAttribute(r._$Eu(e,i))))return;this.C(e,t,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:o},r){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,r??t??this[e]),!0!==o||void 0!==r)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),!0===s&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,i]of e){const{wrapped:e}=i,s=this[t];!0!==e||this._$AL.has(t)||void 0===s||this.C(t,void 0,i,s)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[v("elementProperties")]=new Map,x[v("finalized")]=new Map,g?.({ReactiveElement:x}),(f.reactiveElementVersions??=[]).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const w=globalThis,A=e=>e,k=w.trustedTypes,E=k?k.createPolicy("lit-html",{createHTML:e=>e}):void 0,C="$lit$",S=`lit$${Math.random().toFixed(9).slice(2)}$`,P="?"+S,N=`<${P}>`,O=document,F=()=>O.createComment(""),I=e=>null===e||"object"!=typeof e&&"function"!=typeof e,T=Array.isArray,R="[ \t\n\f\r]",M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,D=/-->/g,H=/>/g,U=RegExp(`>|${R}(?:([^\\s"'>=/]+)(${R}*=${R}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),z=/'/g,j=/"/g,B=/^(?:script|style|textarea|title)$/i,L=(e=>(t,...i)=>({_$litType$:e,strings:t,values:i}))(1),G=Symbol.for("lit-noChange"),K=Symbol.for("lit-nothing"),W=new WeakMap,q=O.createTreeWalker(O,129);function V(e,t){if(!T(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==E?E.createHTML(t):t}class J{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let o=0,r=0;const n=e.length-1,a=this.parts,[l,c]=((e,t)=>{const i=e.length-1,s=[];let o,r=2===t?"<svg>":3===t?"<math>":"",n=M;for(let t=0;t<i;t++){const i=e[t];let a,l,c=-1,d=0;for(;d<i.length&&(n.lastIndex=d,l=n.exec(i),null!==l);)d=n.lastIndex,n===M?"!--"===l[1]?n=D:void 0!==l[1]?n=H:void 0!==l[2]?(B.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=U):void 0!==l[3]&&(n=U):n===U?">"===l[0]?(n=o??M,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?U:'"'===l[3]?j:z):n===j||n===z?n=U:n===D||n===H?n=M:(n=U,o=void 0);const h=n===U&&e[t+1].startsWith("/>")?" ":"";r+=n===M?i+N:c>=0?(s.push(a),i.slice(0,c)+C+i.slice(c)+S+h):i+S+(-2===c?t:h)}return[V(e,r+(e[i]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),s]})(e,t);if(this.el=J.createElement(l,i),q.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(s=q.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes())for(const e of s.getAttributeNames())if(e.endsWith(C)){const t=c[r++],i=s.getAttribute(e).split(S),n=/([.?@])?(.*)/.exec(t);a.push({type:1,index:o,name:n[2],strings:i,ctor:"."===n[1]?ee:"?"===n[1]?te:"@"===n[1]?ie:X}),s.removeAttribute(e)}else e.startsWith(S)&&(a.push({type:6,index:o}),s.removeAttribute(e));if(B.test(s.tagName)){const e=s.textContent.split(S),t=e.length-1;if(t>0){s.textContent=k?k.emptyScript:"";for(let i=0;i<t;i++)s.append(e[i],F()),q.nextNode(),a.push({type:2,index:++o});s.append(e[t],F())}}}else if(8===s.nodeType)if(s.data===P)a.push({type:2,index:o});else{let e=-1;for(;-1!==(e=s.data.indexOf(S,e+1));)a.push({type:7,index:o}),e+=S.length-1}o++}}static createElement(e,t){const i=O.createElement("template");return i.innerHTML=e,i}}function Z(e,t,i=e,s){if(t===G)return t;let o=void 0!==s?i._$Co?.[s]:i._$Cl;const r=I(t)?void 0:t._$litDirective$;return o?.constructor!==r&&(o?._$AO?.(!1),void 0===r?o=void 0:(o=new r(e),o._$AT(e,i,s)),void 0!==s?(i._$Co??=[])[s]=o:i._$Cl=o),void 0!==o&&(t=Z(e,o._$AS(e,t.values),o,s)),t}class Y{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??O).importNode(t,!0);q.currentNode=s;let o=q.nextNode(),r=0,n=0,a=i[0];for(;void 0!==a;){if(r===a.index){let t;2===a.type?t=new Q(o,o.nextSibling,this,e):1===a.type?t=new a.ctor(o,a.name,a.strings,this,e):6===a.type&&(t=new se(o,this,e)),this._$AV.push(t),a=i[++n]}r!==a?.index&&(o=q.nextNode(),r++)}return q.currentNode=O,s}p(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class Q{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=K,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=Z(this,e,t),I(e)?e===K||null==e||""===e?(this._$AH!==K&&this._$AR(),this._$AH=K):e!==this._$AH&&e!==G&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>T(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==K&&I(this._$AH)?this._$AA.nextSibling.data=e:this.T(O.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,s="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=J.createElement(V(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{const e=new Y(s,this),i=e.u(this.options);e.p(t),this.T(i),this._$AH=e}}_$AC(e){let t=W.get(e.strings);return void 0===t&&W.set(e.strings,t=new J(e)),t}k(e){T(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const o of e)s===t.length?t.push(i=new Q(this.O(F()),this.O(F()),this,this.options)):i=t[s],i._$AI(o),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=A(e).nextSibling;A(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class X{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,o){this.type=1,this._$AH=K,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=K}_$AI(e,t=this,i,s){const o=this.strings;let r=!1;if(void 0===o)e=Z(this,e,t,0),r=!I(e)||e!==this._$AH&&e!==G,r&&(this._$AH=e);else{const s=e;let n,a;for(e=o[0],n=0;n<o.length-1;n++)a=Z(this,s[i+n],t,n),a===G&&(a=this._$AH[n]),r||=!I(a)||a!==this._$AH[n],a===K?e=K:e!==K&&(e+=(a??"")+o[n+1]),this._$AH[n]=a}r&&!s&&this.j(e)}j(e){e===K?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class ee extends X{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===K?void 0:e}}class te extends X{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==K)}}class ie extends X{constructor(e,t,i,s,o){super(e,t,i,s,o),this.type=5}_$AI(e,t=this){if((e=Z(this,e,t,0)??K)===G)return;const i=this._$AH,s=e===K&&i!==K||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,o=e!==K&&(i===K||s);s&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class se{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){Z(this,e)}}const oe={I:Q},re=w.litHtmlPolyfillSupport;re?.(J,Q),(w.litHtmlVersions??=[]).push("3.3.3");const ne=globalThis;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */let ae=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{const s=i?.renderBefore??t;let o=s._$litPart$;if(void 0===o){const e=i?.renderBefore??null;s._$litPart$=o=new Q(t.insertBefore(F(),e),e,void 0,i??{})}return o._$AI(e),o})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return G}};ae._$litElement$=!0,ae.finalized=!0,ne.litElementHydrateSupport?.({LitElement:ae});const le=ne.litElementPolyfillSupport;le?.({LitElement:ae}),(ne.litElementVersions??=[]).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ce=e=>(t,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(e,t)}):customElements.define(e,t)},de={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:b},he=(e=de,t,i)=>{const{kind:s,metadata:o}=i;let r=globalThis.litPropertyMetadata.get(o);if(void 0===r&&globalThis.litPropertyMetadata.set(o,r=new Map),"setter"===s&&((e=Object.create(e)).wrapped=!0),r.set(i.name,e),"accessor"===s){const{name:s}=i;return{set(i){const o=t.get.call(this);t.set.call(this,i),this.requestUpdate(s,o,e,!0,i)},init(t){return void 0!==t&&this.C(s,void 0,e,t),t}}}if("setter"===s){const{name:s}=i;return function(i){const o=this[s];t.call(this,i),this.requestUpdate(s,o,e,!0,i)}}throw Error("Unsupported decorator location: "+s)};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function pe(e){return(t,i)=>"object"==typeof i?he(e,t,i):((e,t,i)=>{const s=t.hasOwnProperty(i);return t.constructor.createProperty(i,e),s?Object.getOwnPropertyDescriptor(t,i):void 0})(e,t,i)}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function ue(e){return pe({...e,state:!0,attribute:!1})}const fe="sensor.outdoor_temperature";function me(e,t,i,s){if(!e)return null;const o="fan"===s?'(\n    (state && state.state) ||\n    y\n  ) === "off" ? 0 : 1':function(e){return`(\n    (state && state.attributes && state.attributes.hvac_mode) ||\n    (state && state.state) ||\n    y\n  ) === "${"cooling"===e?"cool":"heat"}" ? 1 : 0`}(s);return{entity:e,filters:[{map_y:o}],name:`$ex '${t}: ' + (Number(ys.at(-1)) === 1 ? 'On' : Number(ys.at(-1)) === 0 ? 'Off' : '—')`,hovertemplate:"%{x|%H:%M}: %{y}<extra></extra>",yaxis:"y2",visible:`$ex hass.states['${e}'] !== undefined`,line:{shape:"hv",color:i,width:1.5}}}function _e(e){return Boolean(e&&e.trim())}function ge(e,t,i="—"){if(!_e(t)||!e.states[t])return i;const s=e.states[t];if("unavailable"===s.state||"unknown"===s.state)return i;const o=s.attributes.unit_of_measurement||"",r=parseFloat(s.state);return Number.isNaN(r)?e.formatEntityState(s):`${Number.isInteger(r)?r:r.toFixed(1)}${o?` ${o}`:""}`}function ve(e,t){if(!_e(t)||!e.states[t])return"—";const i=e.states[t].state;if("unavailable"===i||"unknown"===i)return"—";const s=Math.round(parseFloat(i));return Number.isNaN(s)?"—":`${s} W now`}function ye(e,t){const i=e.states[t];if(!i)return"—";return(i.attributes.hvac_mode||i.state).replace(/_/g," ").replace(/\b\w/g,e=>e.toUpperCase())}function be(e,t){const i=e.states[t];if(!i)return"—";if("off"===i.state)return"Off";const s=i.attributes.percentage;return null!=s?`${s}%`:i.state.replace(/\b\w/g,e=>e.toUpperCase())}function $e(e,t,i){const s=t.split(".")[0];e.callService(s,"set_value",{entity_id:t,value:i})}function xe(e){if(!e||"unknown"===e||"unavailable"===e)return"";const t=e.split(":");return t.length>=2?`${t[0].padStart(2,"0")}:${t[1].padStart(2,"0")}`:e}function we(e,t){e.dispatchEvent(new CustomEvent("hass-more-info",{bubbles:!0,composed:!0,detail:{entityId:t}}))}async function Ae(e,t){if(!await async function(e,t=15e3){if(customElements.get(e))return!0;try{return await Promise.race([customElements.whenDefined(e),new Promise((i,s)=>{setTimeout(()=>s(new Error(`Timed out waiting for ${e}`)),t)})]),!0}catch{return!1}}("plotly-graph"))return null;const{type:i,...s}=t,o=document.createElement("plotly-graph");return o.setConfig(s),o.hass=e,o}function ke(e,t){return e.states[t]}function Ee(e,t,i=0){const s=parseFloat(e.states[t]?.state??"");return Number.isNaN(s)?i:s}function Ce(e,t,i,s){if(!_e(t)||!_e(i))return null;const o=Ee(e,t),r=Ee(e,i,1);return s?o-r:o+r}function Se(e,t,i){e.callService(t.split(".")[0],"set_value",{entity_id:t,value:i})}function Pe(e,t,i,s){const o=ke(e,t);if(!o)return K;const r=Number(o.attributes.min??1),n=Number(o.attributes.max??20),a=Number(o.attributes.step??1),l=Ee(e,t,r);return L`
    <div class="settings-row">
      <div class="settings-row-label-block">
        <span class="settings-row-label">${i}</span>
        ${null!==s?L`<span class="settings-computed">→ ${s.toFixed(0)}°F</span>`:K}
      </div>
      <div class="settings-row-control settings-slider-control">
        <input
          type="range"
          class="settings-slider"
          min=${r}
          max=${n}
          step=${a}
          .value=${String(l)}
          @input=${i=>{const s=parseFloat(i.target.value);Number.isNaN(s)||Se(e,t,s)}}
        />
        <span class="settings-offset-value">${l}°F</span>
      </div>
    </div>
  `}function Ne(e,t,i){const s=Boolean(t.subtractOffsets),o=Ce(e,t.target,t.mediumOffset,s),r=Ce(e,t.target,t.highOffset,s);return L`
    <div class="settings-section">
      <div class="settings-section-title">${t.title}</div>
      ${function(e,t,i){const s=ke(e,t);if(!s)return K;const o=Number(s.attributes.min??0),r=Number(s.attributes.max??100),n=Number(s.attributes.step??1),a=Ee(e,t);return L`
    <div class="settings-row">
      <span class="settings-row-label">${i}</span>
      <div class="settings-row-control settings-target-control">
        <input
          type="number"
          class="settings-target-input"
          min=${o}
          max=${r}
          step=${n}
          .value=${String(a)}
          @change=${i=>{const s=parseFloat(i.target.value);Number.isNaN(s)||Se(e,t,s)}}
        />
        <span class="settings-unit">°F</span>
      </div>
    </div>
  `}(e,t.target,"Target")}
      ${Pe(e,t.mediumOffset,"Medium offset",o)}
      ${Pe(e,t.highOffset,"High offset",r)}
      ${t.deviceButton&&i?L`
            <div class="settings-device-button">
              <button
                type="button"
                class="rcc-btn"
                @click=${e=>i(t.deviceButton,e.target)}
              >
                ${t.deviceButton.name??"Lights & Sound"}
              </button>
            </div>
          `:K}
    </div>
  `}const Oe="room-climate-overlay-styles";class Fe{get isOpen(){return Boolean(this.root)}open(e,t){this._removeDom(),function(){if(document.getElementById(Oe))return;const e=document.createElement("style");e.id=Oe,e.textContent="\n  .rcc-overlay {\n    position: fixed;\n    inset: 0;\n    z-index: 2000;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    background: rgba(0, 0, 0, 0.5);\n    padding: 16px;\n  }\n\n  .rcc-overlay-panel {\n    background: var(--card-background-color, #fff);\n    color: var(--primary-text-color, #212121);\n    border-radius: 12px;\n    width: min(920px, 95vw);\n    max-height: 90vh;\n    overflow: hidden;\n    display: flex;\n    flex-direction: column;\n    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);\n  }\n\n  .rcc-overlay-header {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    padding: 16px 20px 8px;\n    font-size: 1.25rem;\n    font-weight: 500;\n  }\n\n  .rcc-overlay-close {\n    border: none;\n    background: transparent;\n    cursor: pointer;\n    color: inherit;\n    padding: 4px;\n    border-radius: 50%;\n    display: flex;\n  }\n\n  .rcc-overlay-close:hover {\n    background: var(--secondary-background-color, rgba(0, 0, 0, 0.08));\n  }\n\n  .rcc-overlay-body {\n    padding: 0 16px 16px;\n    overflow-y: auto;\n    max-height: calc(90vh - 56px);\n  }\n\n  .rcc-overlay-graph-host {\n    min-height: 400px;\n  }\n\n  .rcc-overlay-power-now {\n    padding: 8px 16px;\n    color: var(--secondary-text-color, #666);\n  }\n",document.head.appendChild(e)}(),this.onClose=t,this.root=document.createElement("div"),this.root.className="rcc-overlay",this.root.addEventListener("click",e=>{e.target===this.root&&this.close()});const i=document.createElement("div");i.className="rcc-overlay-panel";const s=document.createElement("div");s.className="rcc-overlay-header",s.textContent=e;const o=document.createElement("button");return o.className="rcc-overlay-close",o.setAttribute("aria-label","Close"),o.innerHTML='<ha-icon icon="mdi:close"></ha-icon>',o.addEventListener("click",()=>this.close()),s.appendChild(o),this.body=document.createElement("div"),this.body.className="rcc-overlay-body",i.appendChild(s),i.appendChild(this.body),this.root.appendChild(i),document.body.appendChild(this.root),this.body}close(){this._removeDom();const e=this.onClose;this.onClose=void 0,e?.()}_removeDom(){this.root&&(this.root.remove(),this.root=void 0,this.body=void 0)}}const Ie=n`
  :host {
    display: block;
  }

  ha-card {
    overflow: hidden;
  }

  .header {
    text-align: center;
    padding: 16px 16px 8px;
    font-size: 2.25rem;
    font-weight: 700;
    line-height: 1.1;
  }

  .sensor-row {
    display: flex;
    gap: 8px;
    padding: 0 16px 8px;
  }

  .sensor-item {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.05));
  }

  .sensor-label {
    font-size: 0.85rem;
    color: var(--secondary-text-color);
  }

  .sensor-value {
    font-size: 1.1rem;
    font-weight: 500;
    margin-left: auto;
  }

  .devices-section {
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
  }

  .device-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
  }

  .devices-section .device-row:first-child {
    border-top: none;
  }

  .device-toggles {
    flex-shrink: 0;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    gap: 4px;
  }

  .toggle-spacer {
    flex-shrink: 0;
    width: 48px;
  }

  .device-info {
    flex: 1;
    min-width: 0;
    cursor: pointer;
  }

  .device-label {
    font-weight: 500;
  }

  .device-secondary {
    font-size: 0.85rem;
    color: var(--secondary-text-color);
  }

  .device-meta-sep {
    margin: 0 4px;
    color: var(--secondary-text-color);
  }

  .use-toggle {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    width: 48px;
  }

  .use-label {
    font-size: 0.75rem;
    color: var(--secondary-text-color);
  }

  .footer {
    display: flex;
    gap: 8px;
    padding: 12px 16px;
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
  }

  /* Shared button style for card footer and settings dialogs */
  .rcc-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 10px 8px;
    border: none;
    border-radius: 8px;
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.05));
    color: var(--primary-text-color);
    cursor: pointer;
    font: inherit;
  }

  .rcc-btn:hover:not(:disabled) {
    filter: brightness(1.04);
  }

  .rcc-btn:active:not(:disabled) {
    filter: brightness(0.96);
  }

  .rcc-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    filter: none;
  }

  .footer-btn {
    flex: 1;
  }

  .rcc-btn--block {
    width: 100%;
    flex-direction: row;
    font-weight: 500;
  }

  .footer-secondary {
    font-size: 0.7rem;
    color: var(--secondary-text-color);
  }

  ha-dialog {
    --dialog-content-padding: 0;
    --mdc-dialog-max-width: min(920px, 95vw);
  }

  .dialog-body {
    padding: 0 16px 16px;
    max-height: 75vh;
    overflow-y: auto;
  }

  .settings-section {
    margin-bottom: 12px;
    border-radius: var(--ha-card-border-radius, 12px);
    background: var(--card-background-color);
    overflow: hidden;
    box-shadow: var(
      --ha-card-box-shadow,
      0px 2px 1px -1px rgba(0, 0, 0, 0.2),
      0px 1px 1px 0px rgba(0, 0, 0, 0.14),
      0px 1px 3px 0px rgba(0, 0, 0, 0.12)
    );
  }

  .settings-section-title {
    padding: 12px 16px 4px;
    font-size: 1rem;
    font-weight: 500;
    color: var(--primary-text-color);
  }

  .settings-row,
  .settings-readout-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 8px 16px;
    min-height: 48px;
    box-sizing: border-box;
  }

  .settings-readout-row {
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.08));
  }

  .settings-row + .settings-row {
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.08));
  }

  .settings-row-label-block {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .settings-row-label {
    color: var(--primary-text-color);
    font-size: 0.95rem;
  }

  .settings-computed {
    color: var(--secondary-text-color);
    font-size: 0.8rem;
  }

  .settings-readout-value {
    color: var(--primary-text-color);
    font-weight: 500;
  }

  .settings-row-control {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .settings-target-control {
    gap: 4px;
  }

  .settings-target-input {
    width: 4rem;
    text-align: right;
    font: inherit;
    color: inherit;
    background: var(--card-background-color);
    border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.2));
    border-radius: 4px;
    padding: 4px 6px;
  }

  .settings-unit,
  .settings-offset-value {
    color: var(--secondary-text-color);
    font-size: 0.9rem;
    min-width: 2.5rem;
    text-align: right;
  }

  .settings-slider-control {
    min-width: 10rem;
  }

  .settings-slider {
    flex: 1;
    min-width: 6rem;
    accent-color: var(--primary-color, #03a9f4);
  }

  .settings-device-button {
    padding: 8px 16px 12px;
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
    box-sizing: border-box;
  }

  .settings-device-button .rcc-btn {
    box-sizing: border-box;
    max-width: 100%;
  }

  .dialog-graph-host {
    min-height: 400px;
  }

  .power-now {
    padding: 8px 16px;
    color: var(--secondary-text-color);
  }

  .config-error {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 16px;
    color: var(--error-color, #b00020);
  }
`;function Te(e){return e.callWS({type:"room_climate_controller/rooms/list"})}function Re(e){return e.callWS({type:"room_climate_controller/profiles/list"})}let Me=[],De=[],He=!1,Ue=null;const ze=new Set;function je(e){return ze.add(e),()=>ze.delete(e)}async function Be(e){return Ue||(Ue=(async()=>{try{const[t,i]=await Promise.all([Te(e),Re(e)]);Me=t.rooms??[],De=i.profiles??[],He=!0,function(){for(const e of ze)e()}()}catch{}finally{Ue=null}})(),Ue)}function Le(){return Me}function Ge(e){return Me.find(t=>t.key===e)}function Ke(){return Me.map(e=>({key:e.key,label:e.label,has_heating:e.has_heating,has_fan:e.has_fan}))}function We(e){const t=e.entities.presets??{},i={name:Ge(e.room)?.label??e.room,roomKey:e.room,has_heating:e.has_heating,has_fan:e.has_fan,useCooling:t.cooling?.use_entity??void 0,useHeating:t.heating?.use_entity??void 0,useFan:t.fan?.use_entity??void 0,fanOverride:e.entities.fan_override??void 0,cooling:t.cooling?.temp_entity??"",heating:t.heating?.temp_entity??void 0,fan:t.fan?.temp_entity??void 0};return{profileId:e.id,name:e.name,enabled:e.entities.enabled??"",time:e.entities.time??"",roomKey:e.room,room:i}}function qe(e){return De.filter(t=>t.room===e).map(We).sort((e,t)=>{const i=Ve(e.profileId),s=Ve(t.profileId);return i!==s?i.localeCompare(s):e.profileId.localeCompare(t.profileId,void 0,{numeric:!0})})}function Ve(e){return De.find(t=>t.id===e)?.time??"99:99"}const Je={use:null,target:null,medium_offset:null,high_offset:null};function Ze(e){return e.room?.trim()||e.profile_room_key?.trim()||void 0}function Ye(e){const t=Ze(e);if(!t)return;const i=Ge(t);if(!i)return;const s=i.entities,o=e=>s.live[e]??Je,r=o("cooling"),n=o("heating"),a=o("fan");return function(e={}){return{type:"custom:room-climate-control",room_name:"Room",temp_sensor:"",use_ac:"",use_heater:"",use_fan:"",manual_mode:"",target_cooling:"",cooling_medium_offset:"",cooling_high_offset:"",target_heating:"",heating_medium_offset:"",heating_high_offset:"",target_fan:"",fan_medium_offset:"",fan_high_offset:"",outdoor_sensor:fe,time_range:"",...e}}({type:"custom:room-climate-control",room:t,profile_room_key:t,room_name:i.label,temp_sensor:s.temperature??"",humidity_sensor:s.humidity??"",power_sensor:s.power??"",ac_entity:s.ac_entity??"",heater_entity:s.heater_entity??"",fan_entity:s.fan_entity??"",manual_mode:s.manual_mode??"",ac_fan_only_override:s.ac_fan_only_override??"",heater_fan_only_override:s.heater_fan_only_override??"",use_ac:r.use??"",target_cooling:r.target??"",cooling_medium_offset:r.medium_offset??"",cooling_high_offset:r.high_offset??"",use_heater:n.use??"",target_heating:n.target??"",heating_medium_offset:n.medium_offset??"",heating_high_offset:n.high_offset??"",use_fan:a.use??"",target_fan:a.target??"",fan_medium_offset:a.medium_offset??"",fan_high_offset:a.high_offset??"",outdoor_sensor:e.outdoor_sensor??s.outdoor??fe,time_range:e.time_range??s.time_range??"",ac_device_button:e.ac_device_button,heater_device_button:e.heater_device_button,fan_device_button:e.fan_device_button})}let Qe=class extends ae{constructor(){super(...arguments),this._settingsOpen=!1,this._graphDialog=null,this._graphOverlay=new Fe}setConfig(e){if(this._userConfig=e,!Ze(e))return this._config=void 0,void(this._configError="Select a room in the card editor.");this._configError=void 0,this._resolveRoom()}_resolveRoom(){const e=Ye(this._userConfig);if(e)return this._config=e,void(this._configError=void 0);const t=Ze(this._userConfig);Le().length>0&&t&&!function(e){return Le().some(t=>t.key===e)}(t)&&(this._config=void 0,this._configError=`Unknown room "${t}". Add it in the Room Climate integration.`)}getCardSize(){return 6}static getConfigElement(){return document.createElement("room-climate-control-editor")}static getStubConfig(){const e=Le()[0]?.key;return{type:"custom:room-climate-control",room:e??""}}connectedCallback(){super.connectedCallback(),Be(this.hass),this._unsubRooms??=je(()=>{this._resolveRoom(),this.requestUpdate()})}disconnectedCallback(){super.disconnectedCallback(),this._graphOverlay.close(),this._unsubRooms?.(),this._unsubRooms=void 0}updated(e){if(!(e.has("hass")&&this._graphDialog&&this.hass&&this._config))return;this._overlayGraphEl&&(this._overlayGraphEl.hass=this.hass),this._overlayPowerNowEl&&_e(this._config.power_sensor)&&(this._overlayPowerNowEl.textContent=ve(this.hass,this._config.power_sensor));const t=this._config.time_range||"",i=this.hass.states[t]?.state;i&&i!==this._lastGraphHours&&(this._lastGraphHours=i,this._mountGraphOverlay())}render(){if(!this.hass)return L``;if(this._configError)return L`
        <ha-card>
          <div class="config-error">
            <ha-icon icon="mdi:alert-circle"></ha-icon>
            <span>${this._configError}</span>
          </div>
        </ha-card>
      `;if(!this._config)return L`
        <ha-card>
          <div class="config-error">
            <ha-icon icon="mdi:progress-clock"></ha-icon>
            <span>Loading room…</span>
          </div>
        </ha-card>
      `;const e=this._config;return L`
      <ha-card>
        <div class="header">${e.room_name}</div>
        <div class="sensor-row">
          <div class="sensor-item">
            <span class="sensor-label">Temperature</span>
            <span class="sensor-value">${ge(this.hass,e.temp_sensor)}</span>
          </div>
          ${_e(e.humidity_sensor)?L`
                <div class="sensor-item">
                  <span class="sensor-label">Humidity</span>
                  <span class="sensor-value"
                    >${ge(this.hass,e.humidity_sensor)}</span
                  >
                </div>
              `:K}
        </div>

        ${this._renderDevicesPanel(e)}

        <div class="footer">
          <button class="rcc-btn footer-btn" @click=${()=>this._openSettings()}>
            <ha-icon icon="mdi:cog"></ha-icon>
            <span>Settings</span>
          </button>
          <button
            class="rcc-btn footer-btn"
            ?disabled=${!_e(e.power_sensor)}
            @click=${()=>this._openGraphDialog("energy")}
          >
            <ha-icon icon="mdi:flash"></ha-icon>
            <span>Energy Use</span>
            <span class="footer-secondary"
              >${ve(this.hass,e.power_sensor)}</span
            >
          </button>
          <button class="rcc-btn footer-btn" @click=${()=>this._openGraphDialog("history")}>
            <ha-icon icon="mdi:chart-line"></ha-icon>
            <span>History</span>
          </button>
        </div>

        ${this._renderProfilesPanel(e)}
      </ha-card>
      ${this._settingsOpen?this._renderSettingsDialog():K}
    `}_renderProfilesPanel(e){const t=function(e){const t=e.profile_room_key?.trim();if(t)return t;const i=e.manual_mode?.trim();if(i){const e=Le().find(e=>e.entities.manual_mode===i);if(e)return e.key}const s=e.manual_mode?.match(/^input_boolean\.([a-z0-9_]+)_climate_manual_mode$/);return s&&Le().some(e=>e.key===s[1])?s[1]:void 0}(e);return t?L`
      <room-climate-profiles-panel
        .hass=${this.hass}
        .config=${e}
        .roomKey=${t}
      ></room-climate-profiles-panel>
    `:K}_renderDevicesPanel(e){const t=[],i=(e,i,s,o,r,n)=>{if(!_e(i)||!function(e,t){if(!_e(t))return!1;const i=e.states[t];return!!i&&"unavailable"!==i.state&&"unknown"!==i.state}(this.hass,i))return;const a=ke(this.hass,s);if(!a)return;const l=i,c=function(e,t,i=72){const s=e.states[t];if(!s)return i;const o=parseFloat(s.state);return Number.isNaN(o)?i:Math.round(o)}(this.hass,o),d=r(this.hass,l),h=_e(n),p=h?ke(this.hass,n):void 0;t.push(L`
        <div class="device-row">
          <div
            class="device-info"
            role="button"
            tabindex="0"
            @click=${()=>we(this,l)}
            @keydown=${e=>{"Enter"!==e.key&&" "!==e.key||(e.preventDefault(),we(this,l))}}
          >
            <div class="device-label">${e}</div>
            <div class="device-secondary">
              <span>${c}°F target</span>
              <span class="device-meta-sep">·</span>
              <span>${d}</span>
            </div>
          </div>
          <div class="device-toggles">
            ${h&&p?L`
                  <div class="use-toggle">
                    <span class="use-label">Fan Ovr</span>
                    <ha-entity-toggle
                      .hass=${this.hass}
                      .stateObj=${p}
                    ></ha-entity-toggle>
                  </div>
                `:L`<div class="toggle-spacer" aria-hidden="true"></div>`}
            <div class="use-toggle">
              <span class="use-label">Use</span>
              <ha-entity-toggle .hass=${this.hass} .stateObj=${a}></ha-entity-toggle>
            </div>
          </div>
        </div>
      `)},s=_e(e.ac_entity)&&_e(e.heater_entity)&&e.ac_entity===e.heater_entity;if(i("Cooling",e.ac_entity,e.use_ac,e.target_cooling,ye,e.ac_fan_only_override),i("Heating",e.heater_entity,e.use_heater,e.target_heating,ye,s?void 0:e.heater_fan_only_override),i("Fan",e.fan_entity,e.use_fan,e.target_fan,be),0===t.length)return K;const o=ke(this.hass,e.manual_mode);return o&&t.push(L`
        <div class="device-row manual-row">
          <div class="device-info">
            <div class="device-label">Manual Mode</div>
          </div>
          <div class="device-toggles">
            <div class="toggle-spacer" aria-hidden="true"></div>
            <div class="use-toggle">
              <span class="use-label">Use</span>
              <ha-entity-toggle .hass=${this.hass} .stateObj=${o}></ha-entity-toggle>
            </div>
          </div>
        </div>
      `),L`<div class="devices-section">${t}</div>`}_renderSettingsDialog(){if(!this._config)return K;const e=function(e){const t=[];return _e(e.ac_entity)&&t.push({title:"Cooling",target:e.target_cooling,mediumOffset:e.cooling_medium_offset,highOffset:e.cooling_high_offset,deviceButton:e.ac_device_button}),_e(e.heater_entity)&&t.push({title:"Heating",target:e.target_heating,mediumOffset:e.heating_medium_offset,highOffset:e.heating_high_offset,subtractOffsets:!0,deviceButton:e.heater_device_button}),_e(e.fan_entity)&&t.push({title:"Fan",target:e.target_fan,mediumOffset:e.fan_medium_offset,highOffset:e.fan_high_offset,deviceButton:e.fan_device_button}),t}(this._config);return L`
      <ha-dialog
        open
        .heading=${`${this._config.room_name} · Settings`}
        @closed=${this._closeSettings}
        hideActions
      >
        <div class="dialog-body">
          ${function(e,t){const i=[];return _e(t.temp_sensor)&&i.push(L`
      <div class="settings-readout-row">
        <span class="settings-row-label">Temperature</span>
        <span class="settings-readout-value"
          >${ge(e,t.temp_sensor)}</span
        >
      </div>
    `),_e(t.humidity_sensor)&&i.push(L`
      <div class="settings-readout-row">
        <span class="settings-row-label">Humidity</span>
        <span class="settings-readout-value"
          >${ge(e,t.humidity_sensor)}</span
        >
      </div>
    `),0===i.length?K:L`
    <div class="settings-section">
      <div class="settings-section-title">Room</div>
      ${i}
    </div>
  `}(this.hass,this._config)}
          ${e.map(e=>Ne(this.hass,e,(e,t)=>this._onSettingsDeviceButton(e,t)))}
        </div>
      </ha-dialog>
    `}_onSettingsDeviceButton(e,t){t.disabled||(t.disabled=!0,async function(e,t){const i=t.action;if("perform-action"!==i&&"call-service"!==i)return;const s=t.perform_action??t.service;if(!s?.includes("."))return;const[o,r]=s.split(".",2),n={...t.data??{}},a=t.target;void 0!==a?.entity_id&&(n.entity_id=a.entity_id),await e.callService(o,r,n)}(this.hass,e.tap_action).finally(()=>{window.setTimeout(()=>{t.disabled=!1},1e3)}))}_openSettings(){this._closeGraphDialog(),this._settingsOpen=!0}_closeSettings(){this._settingsOpen=!1}_openGraphDialog(e){this._config&&(this._closeSettings(),this._graphDialog=e,this._lastGraphHours=this.hass.states[this._config.time_range||""]?.state,this._mountGraphOverlay())}_closeGraphDialog(){this._graphOverlay.isOpen?this._graphOverlay.close():this._clearGraphDialogState()}_clearGraphDialogState(){this._graphDialog=null,this._lastGraphHours=void 0,this._overlayGraphEl=void 0,this._overlayPowerNowEl=void 0}async _mountGraphOverlay(){if(!this._graphDialog||!this.hass||!this._config)return;const e=this._config,t={energy:`${e.room_name} · Energy Use`,history:`${e.room_name} · History`},i=this._graphOverlay.open(t[this._graphDialog],()=>{this._clearGraphDialogState()});i.innerHTML="",this._overlayGraphEl=void 0,this._overlayPowerNowEl=void 0;const s=e.time_range||"",o=parseInt(this.hass.states[s]?.state||"24",10)||24;if(s){const e=await async function(e,t){if(!window.loadCardHelpers)return null;const i=await window.loadCardHelpers(),s=await i.createCardElement(t);return s&&(s.hass=e),s}(this.hass,function(e){return{type:"entities",entities:[{entity:e,name:"Time range (hours)"}]}}(s));e&&i.appendChild(e)}if("energy"===this._graphDialog){if(_e(e.power_sensor)){const t=document.createElement("div");t.className="rcc-overlay-power-now",t.textContent=ve(this.hass,e.power_sensor),i.appendChild(t),this._overlayPowerNowEl=t}const t=document.createElement("div");t.className="rcc-overlay-graph-host",i.appendChild(t);const r=await Ae(this.hass,function(e,t){return{type:"custom:plotly-graph",hours_to_show:t,refresh_interval:60,config:{displayModeBar:!1,scrollZoom:!1},entities:[{entity:e.power_sensor,filters:["force_numeric"],name:"$ex 'Power: ' + (ys.at(-1) != null ? Math.round(ys.at(-1)) + ' W' : '—')",hovertemplate:"%{x|%H:%M}: %{y:.0f} W<extra></extra>",line:{color:"rgb(255,165,0)",width:2}}],layout:{dragmode:!1,height:400,legend:{orientation:"h",yanchor:"bottom",y:1.02,xanchor:"center",x:.5},margin:{t:40,r:20},yaxis:{title:"Watts",showgrid:!1,zeroline:!1,rangemode:"tozero",fixedrange:!0},xaxis:{showgrid:!1,fixedrange:!0}}}}(e,o));return r?(t.appendChild(r),this._overlayGraphEl=r):t.textContent="Unable to load energy graph (plotly-graph unavailable).",void(this._lastGraphHours=this.hass.states[s]?.state)}const r=document.createElement("div");r.className="rcc-overlay-graph-host",i.appendChild(r);const n=await Ae(this.hass,function(e,t){const i=e.outdoor_sensor||fe,s=[{entity:e.temp_sensor,filters:["force_numeric",{fn:"({ xs, ys, vars }) => {\n            vars._roomTempVals = ys.map(Number).filter((n) => !isNaN(n));\n            return { xs, ys };\n          }"}],name:"$ex 'Room: ' + (ys.at(-1) != null ? ys.at(-1).toFixed(1) + ' °F' : '—')",hovertemplate:"%{x|%H:%M}: %{y:.1f} °F<extra></extra>",yaxis:"y",line:{color:"rgb(255,165,0)",width:2}},{entity:i,filters:["force_numeric",{fn:"({ xs, ys, vars }) => {\n            const outdoor = ys.map(Number).filter((n) => !isNaN(n));\n            const all = [...(vars._roomTempVals || []), ...outdoor];\n            if (all.length) {\n              const dmin = Math.min(...all);\n              const dmax = Math.max(...all);\n              vars.tempYRange = [Math.min(20, dmin) - 1, Math.max(100, dmax) + 1];\n            } else {\n              vars.tempYRange = [20, 100];\n            }\n            return { xs, ys };\n          }"}],name:"$ex 'Outdoor: ' + (ys.at(-1) != null ? ys.at(-1).toFixed(1) + ' °F' : '—')",hovertemplate:"%{x|%H:%M}: %{y:.1f} °F<extra></extra>",yaxis:"y",line:{color:"rgb(100,180,255)",width:2}}],o=me(e.ac_entity,"Cooling","rgb(30,144,255)","cooling"),r=me(e.heater_entity,"Heating","rgb(220,60,60)","heating"),n=me(e.fan_entity,"Fan","rgb(0,180,160)","fan");return o&&s.push(o),r&&s.push(r),n&&s.push(n),{type:"custom:plotly-graph",hours_to_show:t,refresh_interval:60,config:{displayModeBar:!1,scrollZoom:!1},entities:s,layout:{dragmode:!1,height:400,legend:{orientation:"h",yanchor:"bottom",y:1.02,xanchor:"center",x:.5},margin:{t:0,r:60},yaxis:{title:"°F",showgrid:!1,zeroline:!1,range:"$ex vars.tempYRange || [20, 100]",autorange:!1,fixedrange:!0},yaxis2:{title:"State",showgrid:!1,zeroline:!1,overlaying:"y",side:"right",range:[0,1.2],autorange:!1,fixedrange:!0,tickvals:[0,1],ticktext:["Off","On"]},xaxis:{showgrid:!1,fixedrange:!0}}}}(e,o));n?(r.appendChild(n),this._overlayGraphEl=n):r.textContent="Unable to load history graph (plotly-graph unavailable).",this._lastGraphHours=this.hass.states[s]?.state}static get styles(){return Ie}};e([pe({attribute:!1})],Qe.prototype,"hass",void 0),e([ue()],Qe.prototype,"_config",void 0),e([ue()],Qe.prototype,"_configError",void 0),e([ue()],Qe.prototype,"_settingsOpen",void 0),e([ue()],Qe.prototype,"_graphDialog",void 0),Qe=e([ce("room-climate-control")],Qe);const Xe={room:"Room",outdoor_sensor:"Outdoor temperature sensor",time_range:"Graph time-range helper",ac_device_button:"A/C lights & sound button (tap_action)",heater_device_button:"Heater lights & sound button (tap_action)",fan_device_button:"Fan lights & sound button (tap_action)"},et=["outdoor_sensor","time_range","ac_device_button","heater_device_button","fan_device_button"],tt=[{name:"outdoor_sensor",selector:{entity:{filter:[{domain:"sensor",device_class:"temperature"}]}}},{name:"time_range",selector:{entity:{filter:[{domain:"select"},{domain:"input_select"}]}}}],it=[{name:"ac_device_button",selector:{object:{}}},{name:"heater_device_button",selector:{object:{}}},{name:"fan_device_button",selector:{object:{}}}];let st=class extends ae{constructor(){super(...arguments),this._schemaKey="",this._computeLabel=e=>Xe[e.name]||e.name}setConfig(e){this._config={...e,type:"custom:room-climate-control"}}connectedCallback(){super.connectedCallback(),this.hass&&Be(this.hass),this._unsub??=je(()=>this.requestUpdate())}disconnectedCallback(){super.disconnectedCallback(),this._unsub?.(),this._unsub=void 0}_getSchema(e){const t=e.map(e=>e.key).join(",");return this._schema&&t===this._schemaKey||(this._schema=function(e){return[{name:"room",required:!0,selector:{select:{mode:"dropdown",options:e.map(e=>({value:e.key,label:e.label}))}}},...tt,...it]}(e),this._schemaKey=t),this._schema}render(){if(!this.hass||!this._config)return L``;const e=Ke(),t=Ge(this._config.room??"")?.entities,i=function(e,t={}){return{room:e.room??"",outdoor_sensor:e.outdoor_sensor??t.outdoor_sensor??"",time_range:e.time_range??t.time_range??"",ac_device_button:e.ac_device_button,heater_device_button:e.heater_device_button,fan_device_button:e.fan_device_button}}(this._config,{outdoor_sensor:t?.outdoor,time_range:t?.time_range});return L`
      ${0===e.length?L`<div class="hint">
            No Room Climate rooms found. Add a room in Settings → Devices &
            Services → Room Climate first.
          </div>`:L`<div class="hint">
            Pick a room; the card reads its sensors, devices, and helpers from
            the Room Climate integration automatically.
          </div>`}
      <ha-form
        .hass=${this.hass}
        .data=${i}
        .schema=${this._getSchema(e)}
        .computeLabel=${this._computeLabel}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `}_valueChanged(e){e.stopPropagation();const t=e.detail.value,i={...this._config,...t,type:"custom:room-climate-control"},s=i;for(const e of et){const t=s[e];(null==t||""===t||"object"==typeof t&&0===Object.keys(t).length)&&delete s[e]}var o,r;this._config=i,o=this,r=this._config,o.dispatchEvent(new CustomEvent("config-changed",{bubbles:!0,composed:!0,detail:{config:r}}))}static get styles(){return n`
      :host {
        display: block;
        padding: 16px;
      }
      .hint {
        margin-bottom: 12px;
        color: var(--secondary-text-color);
        font-size: 0.9em;
      }
    `}};e([pe({attribute:!1})],st.prototype,"hass",void 0),e([ue()],st.prototype,"_config",void 0),st=e([ce("room-climate-control-editor")],st);
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ot=2;let rt=class{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,i){this._$Ct=e,this._$AM=t,this._$Ci=i}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}};
/**
 * @license
 * Copyright 2020 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const{I:nt}=oe,at=e=>e,lt=()=>document.createComment(""),ct=(e,t,i)=>{const s=e._$AA.parentNode,o=void 0===t?e._$AB:t._$AA;if(void 0===i){const t=s.insertBefore(lt(),o),r=s.insertBefore(lt(),o);i=new nt(t,r,e,e.options)}else{const t=i._$AB.nextSibling,r=i._$AM,n=r!==e;if(n){let t;i._$AQ?.(e),i._$AM=e,void 0!==i._$AP&&(t=e._$AU)!==r._$AU&&i._$AP(t)}if(t!==o||n){let e=i._$AA;for(;e!==t;){const t=at(e).nextSibling;at(s).insertBefore(e,o),e=t}}}return i},dt=(e,t,i=e)=>(e._$AI(t,i),e),ht={},pt=(e,t=ht)=>e._$AH=t,ut=e=>{e._$AR(),e._$AA.remove()},ft=(e,t,i)=>{const s=new Map;for(let o=t;o<=i;o++)s.set(e[o],o);return s},mt=(e=>(...t)=>({_$litDirective$:e,values:t}))(class extends rt{constructor(e){if(super(e),e.type!==ot)throw Error("repeat() can only be used in text expressions")}dt(e,t,i){let s;void 0===i?i=t:void 0!==t&&(s=t);const o=[],r=[];let n=0;for(const t of e)o[n]=s?s(t,n):n,r[n]=i(t,n),n++;return{values:r,keys:o}}render(e,t,i){return this.dt(e,t,i).values}update(e,[t,i,s]){const o=(e=>e._$AH)(e),{values:r,keys:n}=this.dt(t,i,s);if(!Array.isArray(o))return this.ut=n,r;const a=this.ut??=[],l=[];let c,d,h=0,p=o.length-1,u=0,f=r.length-1;for(;h<=p&&u<=f;)if(null===o[h])h++;else if(null===o[p])p--;else if(a[h]===n[u])l[u]=dt(o[h],r[u]),h++,u++;else if(a[p]===n[f])l[f]=dt(o[p],r[f]),p--,f--;else if(a[h]===n[f])l[f]=dt(o[h],r[f]),ct(e,l[f+1],o[h]),h++,f--;else if(a[p]===n[u])l[u]=dt(o[p],r[u]),ct(e,o[h],o[p]),p--,u++;else if(void 0===c&&(c=ft(n,u,f),d=ft(a,h,p)),c.has(a[h]))if(c.has(a[p])){const t=d.get(n[u]),i=void 0!==t?o[t]:null;if(null===i){const t=ct(e,o[h]);dt(t,r[u]),l[u]=t}else l[u]=dt(i,r[u]),ct(e,o[h],i),o[t]=null;u++}else ut(o[p]),p--;else ut(o[h]),h++;for(;u<=f;){const t=ct(e,l[f+1]);dt(t,r[u]),l[u++]=t}for(;h<=p;){const e=o[h++];null!==e&&ut(e)}return this.ut=n,pt(e,l),G}}),_t="daily-routine-climate-temps";
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */let gt=null;function vt(e,t){if(!_e(t))return;const i=parseFloat(e.states[t]?.state??"");return Number.isNaN(i)?void 0:Math.round(i)}function yt(e,t){if(!_e(t))return;const i=e.states[t]?.state;return"on"===i||"off"!==i&&void 0}function bt(e){if(void 0!==e)return"number"==typeof e?{temp:e}:e}function $t(e,t){const i={};for(const s of t){const t={},o=vt(e,s.cooling),r=yt(e,s.useCooling);if(void 0===o&&void 0===r||(t.cooling={temp:o,use:r}),!1!==s.has_heating){const i=vt(e,s.heating),o=yt(e,s.useHeating);void 0===i&&void 0===o||(t.heating={temp:i,use:o})}if(!1!==s.has_fan){const i=vt(e,s.fan),o=yt(e,s.useFan);void 0===i&&void 0===o||(t.fan={temp:i,use:o})}const n=yt(e,s.fanOverride);void 0!==n&&(t.fanOverride=n),i[s.name]=t}return{version:2,type:_t,rooms:i}}async function xt(e){const t=JSON.stringify(e);if(gt=t,navigator.clipboard?.writeText)try{await navigator.clipboard.writeText(t)}catch{}}class wt{constructor(e){this._feedback={},this._timers={},this._onChange=e}get(e){return this._feedback[e]}flash(e,t,i=2e3){void 0!==this._timers[e]&&window.clearTimeout(this._timers[e]),this._feedback={...this._feedback,[e]:t},this._onChange(),this._timers[e]=window.setTimeout(()=>{const t={...this._feedback};delete t[e],this._feedback=t,delete this._timers[e],this._onChange()},i)}dispose(){for(const e of Object.values(this._timers))window.clearTimeout(e);this._timers={},this._feedback={}}}function At(e,t){return qe(t)}function kt(e,t){return e}function Et(e){return Boolean(e&&e.trim())}function Ct(e){const t=e.room;return Et(e.enabled)&&Et(e.time)&&(Et(t.cooling)||Et(t.useCooling)||Et(t.heating)||Et(t.fan))}async function St(e,t,i){const s=function(e,t){const i=Ge(t);if(i)return{name:i.label,roomKey:t,has_heating:i.has_heating,has_fan:i.has_fan,useCooling:e.use_ac,useHeating:i.has_heating?e.use_heater:void 0,useFan:i.has_fan?e.use_fan:void 0,fanOverride:e.ac_fan_only_override,cooling:e.target_cooling,heating:i.has_heating?e.target_heating:void 0,fan:i.has_fan?e.target_fan:void 0}}(t,i);if(!s)return!1;const o=$t(e,[s]);return await xt(o),!0}function Pt(e){const t=e.split(":");return t.length>=2?`${t[0].padStart(2,"0")}:${t[1].padStart(2,"0")}`:e}function Nt(e,t,i,s){const o=Pt(s);for(const s of At(0,t)){if(s.profileId===i)continue;const t=xe(e.states[s.time]?.state);if(t&&t===o)return s}}function Ot(e){const t=(e%1440+1440)%1440,i=Math.floor(t/60),s=t%60;return`${String(i).padStart(2,"0")}:${String(s).padStart(2,"0")}`}function Ft(e,t){const i=function(e,t){const i=new Set;for(const s of At(0,t)){const t=xe(e.states[s.time]?.state);t&&i.add(Pt(t))}return i}(e,t),s=new Date,o=60*s.getHours()+s.getMinutes();let r=15*Math.floor(o/15)+15;r<=o&&(r+=15);for(let e=0;e<96;e++){const e=Ot(r);if(!i.has(e))return e;r+=15}return Ot(r)}const It=n`
  :host {
    display: block;
  }

  .rcc-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 10px 8px;
    border: none;
    border-radius: 8px;
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.05));
    color: var(--primary-text-color);
    cursor: pointer;
    font: inherit;
  }

  .rcc-btn:hover:not(:disabled) {
    filter: brightness(1.04);
  }

  .rcc-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .profiles-section {
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
  }

  .profiles-section-summary {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 14px 16px;
    cursor: pointer;
    list-style: none;
    font-weight: 700;
    font-size: 1.4rem;
    line-height: 1.2;
  }

  .profiles-section-summary::-webkit-details-marker {
    display: none;
  }

  .profiles-count {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--secondary-text-color);
    padding: 2px 8px;
    border-radius: 999px;
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.06));
  }

  .profile-chevron {
    margin-left: auto;
    color: var(--secondary-text-color);
    transition: transform 0.15s ease;
  }

  details[open] > summary .profile-chevron {
    transform: rotate(180deg);
  }

  .profiles-section-body {
    padding: 0 16px 12px;
  }

  .profiles-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
  }

  .profiles-loading-hint {
    font-size: 0.85rem;
    color: var(--warning-color, #ff9800);
    padding: 4px 0 8px;
  }

  .profile-add-error {
    flex: 1 1 100%;
    font-size: 0.85rem;
    color: var(--error-color, #f44336);
    padding: 4px 0;
  }

  .profile-action-btn.success {
    background: var(--success-color, #4caf50);
    color: var(--text-primary-color, #fff);
  }

  .profile-action-btn.error {
    background: var(--error-color, #f44336);
    color: var(--text-primary-color, #fff);
  }

  .profile-time-input.conflict,
  .profile-name-input.field-error {
    border-color: var(--error-color, #f44336);
  }

  .profile-time.duplicate {
    color: var(--error-color, #f44336);
  }

  .profile-item {
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.08));
  }

  .profile-item-summary {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 0;
    cursor: pointer;
    list-style: none;
    font-size: 1.1rem;
    line-height: 1.25;
  }

  .profile-item-summary::-webkit-details-marker {
    display: none;
  }

  .profile-time {
    font-variant-numeric: tabular-nums;
    font-weight: 600;
    width: 5rem;
    flex-shrink: 0;
    text-align: right;
  }

  .profile-short-name {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .profile-item-body {
    padding: 0 0 12px;
  }

  .profile-name-field {
    display: block;
    margin-bottom: 8px;
  }

  .profile-name-field .profile-name-input {
    width: 100%;
    max-width: 20rem;
    box-sizing: border-box;
  }

  .profile-schedule {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: flex-end;
    margin-bottom: 8px;
  }

  .profile-field-label {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 0.8rem;
    color: var(--secondary-text-color);
  }

  .profile-name-input,
  .profile-time-input {
    font: inherit;
    padding: 6px 8px;
    border-radius: 6px;
    border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.2));
    background: var(--card-background-color);
    color: var(--primary-text-color);
  }

  .profile-add-name {
    flex: 1;
    min-width: 140px;
  }

  .profile-add-time {
    flex-shrink: 0;
  }

  .profile-enable {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .profile-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
  }

  .profile-action-btn {
    flex-direction: row;
    padding: 6px 10px;
    font-size: 0.85rem;
    gap: 4px;
    min-width: 6.25rem;
    box-sizing: border-box;
    justify-content: center;
  }

  .profile-action-btn > span {
    min-width: 3.25rem;
    text-align: center;
  }

  .profile-action-btn.primary {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
  }

  .profile-action-btn.danger {
    color: var(--error-color, #f44336);
  }

  .profile-device-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
  }

  .profile-device-label {
    width: 4.5rem;
    flex-shrink: 0;
    font-size: 0.9rem;
  }

  .profile-device-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    flex: 1;
  }

  .profile-use {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .profile-use-label {
    font-size: 0.7rem;
    color: var(--secondary-text-color);
  }

  .profile-temp {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .profile-temp-input {
    width: 3.5rem;
    text-align: right;
    font: inherit;
    padding: 4px 6px;
    border-radius: 4px;
    border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.2));
    background: var(--card-background-color);
    color: var(--primary-text-color);
  }

  .profile-temp-unit {
    font-size: 0.85rem;
    color: var(--secondary-text-color);
  }

  .profile-hint {
    font-size: 0.85rem;
    color: var(--secondary-text-color);
    padding: 8px 0;
  }
`;let Tt=class extends ae{constructor(){super(...arguments),this._profilesOpen=!1,this._busy=!1,this._newProfileName="",this._newProfileTime="06:00",this._showAddForm=!1,this._addError="",this._renameDrafts={},this._feedbackVersion=0,this._fieldFeedback={},this._openProfileIds=new Set,this._focusAddName=!1,this._pasteRoomSettingsOnCreate=!1,this._buttonFeedback=new wt(()=>{this._feedbackVersion+=1})}connectedCallback(){super.connectedCallback(),this._unsubStore=je(()=>this.requestUpdate()),Be(this.hass)}disconnectedCallback(){super.disconnectedCallback(),this._unsubStore?.(),this._unsubStore=void 0,this._buttonFeedback.dispose()}_routines(){return qe(this.roomKey)}_flashField(e,t){this._fieldFeedback={...this._fieldFeedback,[e]:t},window.setTimeout(()=>{if(this._fieldFeedback[e]!==t)return;const i={...this._fieldFeedback};delete i[e],this._fieldFeedback=i},2e3)}_btnFeedback(e){return this._feedbackVersion,this._buttonFeedback.get(e)}updated(e){if(super.updated(e),this._focusAddName&&this.shadowRoot&&(this._focusAddName=!1,requestAnimationFrame(()=>{const e=this.shadowRoot?.querySelector(".profile-add-name");e?.focus()})),!this._focusTarget||!this.shadowRoot)return;const{profileId:t,selector:i}=this._focusTarget,s=new Set(this._openProfileIds);s.add(t),this._openProfileIds=s,requestAnimationFrame(()=>{const e=this.shadowRoot?.querySelector(i);e?.focus(),this._focusTarget=void 0})}_renderActionButton(e,t,i,s,o={}){const r=this._btnFeedback(e),n="success"===r?"mdi:check":"error"===r?"mdi:alert-circle-outline":i;return L`
      <button
        type="button"
        class="rcc-btn profile-action-btn ${o.primary?"primary":""} ${o.danger?"danger":""} ${r??""}"
        ?disabled=${this._busy}
        @click=${()=>{s()}}
      >
        <ha-icon icon=${n}></ha-icon>
        <span>${t}</span>
      </button>
    `}_renderDeviceRow(e,t,i,s){const o=_e(i)?ke(this.hass,i):void 0,r=_e(t)?ke(this.hass,t):void 0,n=_e(s)?ke(this.hass,s):void 0;if(!o&&!r&&!n)return K;const a=Number(o?.attributes.min??0),l=Number(o?.attributes.max??100),c=Number(o?.attributes.step??1),d=o?parseFloat(o.state):NaN,h=Number.isNaN(d)?"":String(Math.round(d));return L`
      <div class="profile-device-row">
        <span class="profile-device-label">${e}</span>
        <div class="profile-device-controls">
          ${n?L`
                <div class="profile-use">
                  <span class="profile-use-label">Fan Ovr</span>
                  <ha-entity-toggle .hass=${this.hass} .stateObj=${n}></ha-entity-toggle>
                </div>
              `:K}
          ${r?L`
                <div class="profile-use">
                  <span class="profile-use-label">Use</span>
                  <ha-entity-toggle .hass=${this.hass} .stateObj=${r}></ha-entity-toggle>
                </div>
              `:K}
          ${o?L`
                <div class="profile-temp">
                  <input
                    type="number"
                    class="profile-temp-input"
                    min=${a}
                    max=${l}
                    step=${c}
                    .value=${h}
                    @change=${e=>{const t=parseFloat(e.target.value);Number.isNaN(t)||$e(this.hass,i,t)}}
                  />
                  <span class="profile-temp-unit">°F</span>
                </div>
              `:K}
        </div>
      </div>
    `}_renderRoom(e){return e.roomKey?L`
      <div class="profile-room-block">
        ${this._renderDeviceRow("Cooling",e.useCooling,e.cooling,e.fanOverride)}
        ${!1!==e.has_heating?this._renderDeviceRow("Heating",e.useHeating,e.heating):K}
        ${!1!==e.has_fan?this._renderDeviceRow("Fan",e.useFan,e.fan):K}
      </div>
    `:L`<div class="profile-hint">Preset entities loading… refresh in a moment.</div>`}async _copyProfile(e){const t=`copy-${e.profileId}`;try{const i=$t(this.hass,[e.room]);await xt(i),this._buttonFeedback.flash(t,"success",1500)}catch{this._buttonFeedback.flash(t,"error")}}async _pasteRoutine(e){const t=`paste-${e.profileId}`,i=await async function(){if(navigator.clipboard?.readText)try{const e=await navigator.clipboard.readText();if(e?.trim())return gt=e,e}catch{}return gt}();if(!i)return void this._buttonFeedback.flash(t,"error");const s=function(e){try{const t=JSON.parse(e);if((1===t?.version||2===t?.version)&&t?.type===_t&&t.rooms&&"object"==typeof t.rooms)return t}catch{}return null}(i);if(!s)return void this._buttonFeedback.flash(t,"error");const o=function(e,t,i,s,o){let r=0;for(const e of t){const t=i.rooms[e.name];if(!t)continue;void 0!==t.fanOverride&&_e(e.fanOverride)&&(o(e.fanOverride,t.fanOverride),r++);const n=[{key:"cooling",useId:e.useCooling,tempId:e.cooling,enabled:!0},{key:"heating",useId:e.useHeating,tempId:e.heating,enabled:!1!==e.has_heating},{key:"fan",useId:e.useFan,tempId:e.fan,enabled:!1!==e.has_fan}];for(const e of n){if(!e.enabled)continue;const i=bt("cooling"===e.key?t.cooling:"heating"===e.key?t.heating:t.fan);i&&(void 0!==i.use&&_e(e.useId)&&(o(e.useId,i.use),r++),void 0!==i.temp&&_e(e.tempId)&&(s(e.tempId,i.temp),r++))}}return r}(this.hass,[e.room],s,(e,t)=>$e(this.hass,e,t),(e,t)=>function(e,t,i){const s=t.split(".")[0];e.callService(s,i?"turn_on":"turn_off",{entity_id:t})}(this.hass,e,t));0!==o?this._buttonFeedback.flash(t,"success"):this._buttonFeedback.flash(t,"error")}async _copyCurrentRoom(){const e="copy-room";try{const t=await St(this.hass,this.config,this.roomKey);t&&this._showAddForm&&(this._pasteRoomSettingsOnCreate=!0),this._buttonFeedback.flash(e,t?"success":"error",1500)}catch{this._buttonFeedback.flash(e,"error")}}async _applyNow(e){const t=`apply-${e.profileId}`;this._busy=!0;try{await(i=this.hass,s=e.profileId,i.callWS({type:"room_climate_controller/profiles/apply",profile_id:s})),this._buttonFeedback.flash(t,"success")}catch{this._buttonFeedback.flash(t,"error")}finally{this._busy=!1}var i,s}_renameValue(e){return void 0!==this._renameDrafts[e.profileId]?this._renameDrafts[e.profileId]:kt(e.name,e.profileId)}_savedProfileName(e){return kt(e.name,e.profileId)}async _commitProfileName(e,t){const i=t.trim(),s=this._savedProfileName(e),o=`name-${e.profileId}`;if(i===s){const t={...this._renameDrafts};return delete t[e.profileId],void(this._renameDrafts=t)}if(!i){const t={...this._renameDrafts};return delete t[e.profileId],this._renameDrafts=t,void this._flashField(o,"error")}this._busy=!0;try{await function(e,t,i){return e.callWS({type:"room_climate_controller/profiles/rename",profile_id:t,name:i})}(this.hass,e.profileId,i);const t={...this._renameDrafts};delete t[e.profileId],this._renameDrafts=t,await Be(this.hass),this._flashField(o,"success")}catch{this._flashField(o,"error")}finally{this._busy=!1}}async _setProfileTime(e,t){const i=`time-${e.profileId}`;var s,o,r;if(Nt(this.hass,this.roomKey,e.profileId,t))this._flashField(i,"error");else if(_e(e.time))try{await(s=this.hass,o=e.time,r=`${t}:00`,"input_datetime"===o.split(".")[0]?s.callService("input_datetime","set_datetime",{entity_id:o,time:r}):s.callService("time","set_value",{entity_id:o,time:r})),await Be(this.hass),this._flashField(i,"success")}catch{this._flashField(i,"error")}}_timeConflictMessage(e){const t=Nt(this.hass,this.roomKey,"",e);if(!t)return"Another profile in this room already uses that time.";return`“${kt(t.name,t.profileId)}” already runs at ${e} in this room.`}async _addProfile(){const e="add-profile",t="add-profile-time",i=this._newProfileName.trim(),s=Pt(this._newProfileTime);if(this._addError="",!i)return this._addError="Enter a profile name.",void this._buttonFeedback.flash(e,"error");if(!s)return this._addError="Choose a valid time.",void this._flashField(t,"error");if(Nt(this.hass,this.roomKey,"",s))return this._addError=this._timeConflictMessage(s),void this._flashField(t,"error");this._busy=!0;try{const t=await(o=this.hass,r={name:i,room:this.roomKey,time:s,copy_room_settings:this._pasteRoomSettingsOnCreate},o.callWS({type:"room_climate_controller/profiles/create",...r}));await Be(this.hass),this._pasteRoomSettingsOnCreate=!1;const n=t.profile?.id;n&&(this._openProfileIds=new Set([...this._openProfileIds,n])),this._newProfileName="",this._newProfileTime=Ft(this.hass,this.roomKey),this._showAddForm=!1,this._addError="",this._buttonFeedback.flash(e,"success")}catch(t){this._addError=function(e){if(e&&"object"==typeof e&&"message"in e){const t=e.message;if("string"==typeof t)return t.trim()}return""}(t)||"Could not create profile. Check Settings → System → Logs.",this._buttonFeedback.flash(e,"error")}finally{this._busy=!1}var o,r}async _deleteProfile(e){const t=`delete-${e.profileId}`,i=kt(e.name,e.profileId);if(window.confirm(`Delete profile “${i}”?`)){this._busy=!0;try{await(s=this.hass,o=e.profileId,s.callWS({type:"room_climate_controller/profiles/delete",profile_id:o}));const i=new Set(this._openProfileIds);i.delete(e.profileId),this._openProfileIds=i,await Be(this.hass),this._buttonFeedback.flash(t,"success",800)}catch{this._buttonFeedback.flash(t,"error")}finally{this._busy=!1}var s,o}}_renderProfile(e){const t=_e(e.time)?xe(this.hass.states[e.time]?.state):"",i=kt(e.name,e.profileId),s=function(e,t){const i=xe(e.states[t.time]?.state);return!!i&&Boolean(Nt(e,t.roomKey,t.profileId,i))}(this.hass,e),o=`time-${e.profileId}`,r=`name-${e.profileId}`;return L`
      <details
        class="profile-item"
        .open=${this._openProfileIds.has(e.profileId)}
        @toggle=${t=>{const i=t.target,s=new Set(this._openProfileIds);i.open?s.add(e.profileId):s.delete(e.profileId),this._openProfileIds=s}}
      >
        <summary class="profile-item-summary">
          <span class="profile-time ${s?"duplicate":""}"
            >${t?function(e){if(!e)return"";const t=e.split(":");if(t.length<2)return e;const i=parseInt(t[0],10),s=t[1].padStart(2,"0").slice(0,2);return Number.isNaN(i)?e:`${i%12==0?12:i%12}:${s} ${i>=12?"PM":"AM"}`}(t):"—:—"}</span
          >
          <span class="profile-short-name">${i}</span>
          <span class="profile-chevron">▼</span>
        </summary>
        <div class="profile-item-body">
          <label class="profile-field-label profile-name-field">
            Name
            <input
              type="text"
              class="profile-name-input ${"error"===this._fieldFeedback[r]?"field-error":""}"
              .value=${this._renameValue(e)}
              ?disabled=${this._busy}
              @input=${t=>{this._renameDrafts={...this._renameDrafts,[e.profileId]:t.target.value}}}
              @change=${t=>{this._commitProfileName(e,t.target.value)}}
              @keydown=${t=>{"Enter"===t.key&&(t.preventDefault(),this._commitProfileName(e,t.target.value))}}
            />
          </label>
          <div class="profile-schedule">
            <label class="profile-field-label">
              Time
              <input
                id="profile-time-${e.profileId}"
                type="time"
                class="profile-time-input ${"error"===this._fieldFeedback[o]?"conflict":""}"
                .value=${t}
                ?disabled=${this._busy}
                @blur=${t=>{const i=t.target.value;i&&this._setProfileTime(e,i)}}
                @keydown=${t=>{if("Enter"===t.key){t.preventDefault();const i=t.target.value;i&&this._setProfileTime(e,i)}}}
              />
            </label>
            <div class="profile-enable">
              <span class="profile-field-label">Enabled</span>
              ${_e(e.enabled)&&ke(this.hass,e.enabled)?L`
                    <ha-entity-toggle
                      .hass=${this.hass}
                      .stateObj=${ke(this.hass,e.enabled)}
                    ></ha-entity-toggle>
                  `:K}
            </div>
          </div>
          <div class="profile-actions">
            ${this._renderActionButton(`apply-${e.profileId}`,"Apply now","mdi:check-circle-outline",()=>this._applyNow(e),{primary:!0})}
            ${this._renderActionButton(`copy-${e.profileId}`,"Copy","mdi:content-copy",()=>this._copyProfile(e))}
            ${this._renderActionButton(`paste-${e.profileId}`,"Paste","mdi:content-paste",()=>this._pasteRoutine(e))}
            ${this._renderActionButton(`delete-${e.profileId}`,"Delete","mdi:delete-outline",()=>this._deleteProfile(e),{danger:!0})}
          </div>
          ${this._renderRoom(e.room)}
        </div>
      </details>
    `}_renderToolbar(){return L`
      <div class="profiles-toolbar">
        ${this._renderActionButton("copy-room",this._showAddForm?"Use room settings":"Copy room","mdi:clipboard-arrow-up-outline",()=>this._copyCurrentRoom())}
        ${this._showAddForm?L`
              <input
                type="text"
                class="profile-name-input profile-add-name"
                placeholder="Profile name"
                .value=${this._newProfileName}
                ?disabled=${this._busy}
                @input=${e=>{this._newProfileName=e.target.value,this._addError=""}}
                @keydown=${e=>{"Enter"===e.key&&this._addProfile()}}
              />
              <label class="profile-field-label profile-add-time">
                Time
                <input
                  type="time"
                  class="profile-time-input ${"error"===this._fieldFeedback["add-profile-time"]?"conflict":""}"
                  .value=${this._newProfileTime}
                  ?disabled=${this._busy}
                  @input=${e=>{this._newProfileTime=e.target.value,this._addError=""}}
                />
              </label>
              ${this._renderActionButton("add-profile","Create","mdi:plus",()=>this._addProfile(),{primary:!0})}
              <button
                type="button"
                class="rcc-btn profile-action-btn"
                ?disabled=${this._busy}
                @click=${()=>{this._showAddForm=!1,this._newProfileName="",this._newProfileTime=Ft(this.hass,this.roomKey),this._addError="",this._pasteRoomSettingsOnCreate=!1}}
              >
                <span>Cancel</span>
              </button>
              ${this._addError?L`<div class="profile-add-error" role="alert">${this._addError}</div>`:K}
            `:L`
              <button
                type="button"
                class="rcc-btn profile-action-btn"
                ?disabled=${this._busy}
                @click=${()=>{this._newProfileName="",this._newProfileTime=Ft(this.hass,this.roomKey),this._addError="",this._pasteRoomSettingsOnCreate=!1,this._showAddForm=!0,this._focusAddName=!0}}
              >
                <ha-icon icon="mdi:plus"></ha-icon>
                <span>Add</span>
              </button>
            `}
      </div>
    `}render(){const e=this._routines(),t=e.filter(Ct);return L`
      <details
        class="profiles-section"
        ?open=${this._profilesOpen}
        @toggle=${e=>{this._profilesOpen=e.target.open}}
      >
        <summary class="profiles-section-summary">
          <span>Profiles</span>
          <span class="profiles-count">${e.length}</span>
          <span class="profile-chevron">▼</span>
        </summary>
        <div class="profiles-section-body">
          ${this._renderToolbar()}
          ${t.length<e.length?L`<div class="profiles-loading-hint">
                Some profiles are still loading after a reload.
              </div>`:K}
          ${0===e.length?L`<div class="profile-hint">No profiles for this room yet.</div>`:mt(e,e=>e.profileId,e=>this._renderProfile(e))}
        </div>
      </details>
    `}static get styles(){return It}};e([pe({attribute:!1})],Tt.prototype,"hass",void 0),e([pe({attribute:!1})],Tt.prototype,"config",void 0),e([pe({attribute:!1})],Tt.prototype,"roomKey",void 0),e([ue()],Tt.prototype,"_profilesOpen",void 0),e([ue()],Tt.prototype,"_busy",void 0),e([ue()],Tt.prototype,"_newProfileName",void 0),e([ue()],Tt.prototype,"_newProfileTime",void 0),e([ue()],Tt.prototype,"_showAddForm",void 0),e([ue()],Tt.prototype,"_addError",void 0),e([ue()],Tt.prototype,"_renameDrafts",void 0),e([ue()],Tt.prototype,"_feedbackVersion",void 0),e([ue()],Tt.prototype,"_fieldFeedback",void 0),e([ue()],Tt.prototype,"_openProfileIds",void 0),e([ue()],Tt.prototype,"_focusTarget",void 0),e([ue()],Tt.prototype,"_focusAddName",void 0),e([ue()],Tt.prototype,"_pasteRoomSettingsOnCreate",void 0),Tt=e([ce("room-climate-profiles-panel")],Tt),window.customCards=window.customCards||[],window.customCards.push({type:"room-climate-control",name:"Room Climate Control",description:"Per-room climate dashboard card wired to a room's backend helpers and devices.",preview:!0}),console.info("%c ROOM-CLIMATE-CONTROL %c v1.4.23 ","color: white; background: #0288d1; font-weight: 700;","color: #0288d1; background: white; font-weight: 700;");
//# sourceMappingURL=room-climate-control-card.js.map

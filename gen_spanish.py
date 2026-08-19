# -*- coding: utf-8 -*-
"""
生成西班牙语动词变位表网页（verbo-espanol.html，自包含单文件）
- 变位引擎：规则动词 + 词干变化(e>ie/o>ue/e>i/u>ue) + 拼写修正(gar/car/zar/ger/gir/cer/cir/guir/quir)
  + -uir 类 + -ducir 类 + -eer(y) + 完全不规则模型 + 前缀派生
- 时态：陈述式(7) 虚拟式(5) 命令式(2) 非人称(3) = 17 组
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "verbo-espanol.html")

# ---------------------------------------------------------------------------
HABER = {
    "pres": ["he", "has", "ha", "hemos", "habéis", "han"],
    "imperf": ["había", "habías", "había", "habíamos", "habíais", "habían"],
    "subj_pres": ["haya", "hayas", "haya", "hayamos", "hayáis", "hayan"],
    "subj_imp": ["hubiera", "hubieras", "hubiera", "hubiéramos", "hubierais", "hubieran"],
}

# ---------------------------------------------------------------------------
# Modelos totalmente irregulares
# ---------------------------------------------------------------------------
MODELS = {
    "haber": dict(pres=["he","has","ha","hemos","habéis","han"],
        imperf=["había","habías","había","habíamos","habíais","habían"],
        indef=["hube","hubiste","hubo","hubimos","hubisteis","hubieron"],
        fut=["habré","habrás","habrá","habremos","habréis","habrán"],
        cond=["habría","habrías","habría","habríamos","habríais","habrían"],
        subj_pres=["haya","hayas","haya","hayamos","hayáis","hayan"],
        subj_imp=["hubiera","hubieras","hubiera","hubiéramos","hubierais","hubieran"],
        imp_aff=["","he","haya","hayamos","habed","hayan"],
        inf="haber", ger="habiendo", pp="habido"),
    "tener": dict(pres=["tengo","tienes","tiene","tenemos","tenéis","tienen"],
        imperf=["tenía","tenías","tenía","teníamos","teníais","tenían"],
        indef=["tuve","tuviste","tuvo","tuvimos","tuvisteis","tuvieron"],
        fut=["tendré","tendrás","tendrá","tendremos","tendréis","tendrán"],
        cond=["tendría","tendrías","tendría","tendríamos","tendríais","tendrían"],
        subj_pres=["tenga","tengas","tenga","tengamos","tengáis","tengan"],
        subj_imp=["tuviera","tuvieras","tuviera","tuviéramos","tuvierais","tuvieran"],
        imp_aff=["","ten","tenga","tengamos","tened","tengan"],
        inf="tener", ger="teniendo", pp="tenido"),
    "venir": dict(pres=["vengo","vienes","viene","venimos","venís","vienen"],
        imperf=["venía","venías","venía","veníamos","veníais","venían"],
        indef=["vine","viniste","vino","vinimos","vinisteis","vinieron"],
        fut=["vendré","vendrás","vendrá","vendremos","vendréis","vendrán"],
        cond=["vendría","vendrías","vendría","vendríamos","vendríais","vendrían"],
        subj_pres=["venga","vengas","venga","vengamos","vengáis","vengan"],
        subj_imp=["viniera","vinieras","viniera","viniéramos","vinierais","vinieran"],
        imp_aff=["","ven","venga","vengamos","venid","vengan"],
        inf="venir", ger="viniendo", pp="venido"),
    "decir": dict(pres=["digo","dices","dice","decimos","decís","dicen"],
        imperf=["decía","decías","decía","decíamos","decíais","decían"],
        indef=["dije","dijiste","dijo","dijimos","dijisteis","dijeron"],
        fut=["diré","dirás","dirá","diremos","diréis","dirán"],
        cond=["diría","dirías","diría","diríamos","diríais","dirían"],
        subj_pres=["diga","digas","diga","digamos","digáis","digan"],
        subj_imp=["dijera","dijeras","dijera","dijéramos","dijerais","dijeran"],
        imp_aff=["","di","diga","digamos","decid","digan"],
        inf="decir", ger="diciendo", pp="dicho"),
    "hacer": dict(pres=["hago","haces","hace","hacemos","hacéis","hacen"],
        imperf=["hacía","hacías","hacía","hacíamos","hacíais","hacían"],
        indef=["hice","hiciste","hizo","hicimos","hicisteis","hicieron"],
        fut=["haré","harás","hará","haremos","haréis","harán"],
        cond=["haría","harías","haría","haríamos","haríais","harían"],
        subj_pres=["haga","hagas","haga","hagamos","hagáis","hagan"],
        subj_imp=["hiciera","hicieras","hiciera","hiciéramos","hicierais","hicieran"],
        imp_aff=["","haz","haga","hagamos","haced","hagan"],
        inf="hacer", ger="haciendo", pp="hecho"),
    "poner": dict(pres=["pongo","pones","pone","ponemos","ponéis","ponen"],
        imperf=["ponía","ponías","ponía","poníamos","poníais","ponían"],
        indef=["puse","pusiste","puso","pusimos","pusisteis","pusieron"],
        fut=["pondré","pondrás","pondrá","pondremos","pondréis","pondrán"],
        cond=["pondría","pondrías","pondría","pondríamos","pondríais","pondrían"],
        subj_pres=["ponga","pongas","ponga","pongamos","pongáis","pongan"],
        subj_imp=["pusiera","pusieras","pusiera","pusiéramos","pusierais","pusieran"],
        imp_aff=["","pon","ponga","pongamos","poned","pongan"],
        inf="poner", ger="poniendo", pp="puesto"),
    "querer": dict(pres=["quiero","quieres","quiere","queremos","queréis","quieren"],
        imperf=["quería","querías","quería","queríamos","queríais","querían"],
        indef=["quise","quisiste","quiso","quisimos","quisisteis","quisieron"],
        fut=["querré","querrás","querrá","querremos","querréis","querrán"],
        cond=["querría","querrías","querría","querríamos","querríais","querrían"],
        subj_pres=["quiera","quieras","quiera","queramos","queráis","quieran"],
        subj_imp=["quisiera","quisieras","quisiera","quisiéramos","quisierais","quisieran"],
        imp_aff=["","quiere","quiera","queramos","quered","quieran"],
        inf="querer", ger="queriendo", pp="querido"),
    "saber": dict(pres=["sé","sabes","sabe","sabemos","sabéis","saben"],
        imperf=["sabía","sabías","sabía","sabíamos","sabíais","sabían"],
        indef=["supe","supiste","supo","supimos","supisteis","supieron"],
        fut=["sabré","sabrás","sabrá","sabremos","sabréis","sabrán"],
        cond=["sabría","sabrías","sabría","sabríamos","sabríais","sabrían"],
        subj_pres=["sepa","sepas","sepa","sepamos","sepáis","sepan"],
        subj_imp=["supiera","supieras","supiera","supiéramos","supierais","supieran"],
        imp_aff=["","sabe","sepa","sepamos","sabed","sepan"],
        inf="saber", ger="sabiendo", pp="sabido"),
    "poder": dict(pres=["puedo","puedes","puede","podemos","podéis","pueden"],
        imperf=["podía","podías","podía","podíamos","podíais","podían"],
        indef=["pude","pudiste","pudo","pudimos","pudisteis","pudieron"],
        fut=["podré","podrás","podrá","podremos","podréis","podrán"],
        cond=["podría","podrías","podría","podríamos","podríais","podrían"],
        subj_pres=["pueda","puedas","pueda","podamos","podáis","puedan"],
        subj_imp=["pudiera","pudieras","pudiera","pudiéramos","pudierais","pudieran"],
        imp_aff=["","puede","pueda","podamos","poded","puedan"],
        inf="poder", ger="pudiendo", pp="podido"),
    "dar": dict(pres=["doy","das","da","damos","dais","dan"],
        imperf=["daba","dabas","daba","dábamos","dabais","daban"],
        indef=["di","diste","dio","dimos","disteis","dieron"],
        fut=["daré","darás","dará","daremos","daréis","darán"],
        cond=["daría","darías","daría","daríamos","daríais","darían"],
        subj_pres=["dé","des","dé","demos","deis","den"],
        subj_imp=["diera","dieras","diera","diéramos","dierais","dieran"],
        imp_aff=["","da","dé","demos","dad","den"],
        inf="dar", ger="dando", pp="dado"),
    "ver": dict(pres=["veo","ves","ve","vemos","veis","ven"],
        imperf=["veía","veías","veía","veíamos","veíais","veían"],
        indef=["vi","viste","vio","vimos","visteis","vieron"],
        fut=["veré","verás","verá","veremos","veréis","verán"],
        cond=["vería","verías","vería","veríamos","veríais","verían"],
        subj_pres=["vea","veas","vea","veamos","veáis","vean"],
        subj_imp=["viera","vieras","viera","viéramos","vierais","vieran"],
        imp_aff=["","ve","vea","veamos","ved","vean"],
        inf="ver", ger="viendo", pp="visto"),
    "ir": dict(pres=["voy","vas","va","vamos","vais","van"],
        imperf=["iba","ibas","iba","íbamos","ibais","iban"],
        indef=["fui","fuiste","fue","fuimos","fuisteis","fueron"],
        fut=["iré","irás","irá","iremos","iréis","irán"],
        cond=["iría","irías","iría","iríamos","iríais","irían"],
        subj_pres=["vaya","vayas","vaya","vayamos","vayáis","vayan"],
        subj_imp=["fuera","fueras","fuera","fuéramos","fuerais","fueran"],
        imp_aff=["","ve","vaya","vamos","id","vayan"],
        inf="ir", ger="yendo", pp="ido"),
    "ser": dict(pres=["soy","eres","es","somos","sois","son"],
        imperf=["era","eras","era","éramos","erais","eran"],
        indef=["fui","fuiste","fue","fuimos","fuisteis","fueron"],
        fut=["seré","serás","será","seremos","seréis","serán"],
        cond=["sería","serías","sería","seríamos","seríais","serían"],
        subj_pres=["sea","seas","sea","seamos","seáis","sean"],
        subj_imp=["fuera","fueras","fuera","fuéramos","fuerais","fueran"],
        imp_aff=["","sé","sea","seamos","sed","sean"],
        inf="ser", ger="siendo", pp="sido"),
    "estar": dict(pres=["estoy","estás","está","estamos","estáis","están"],
        imperf=["estaba","estabas","estaba","estábamos","estabais","estaban"],
        indef=["estuve","estuviste","estuvo","estuvimos","estuvisteis","estuvieron"],
        fut=["estaré","estarás","estará","estaremos","estaréis","estarán"],
        cond=["estaría","estarías","estaría","estaríamos","estaríais","estarían"],
        subj_pres=["esté","estés","esté","estemos","estéis","estén"],
        subj_imp=["estuviera","estuvieras","estuviera","estuviéramos","estuvierais","estuvieran"],
        imp_aff=["","está","esté","estemos","estad","estén"],
        inf="estar", ger="estando", pp="estado"),
    "traer": dict(pres=["traigo","traes","trae","traemos","traéis","traen"],
        imperf=["traía","traías","traía","traíamos","traíais","traían"],
        indef=["traje","trajiste","trajo","trajimos","trajisteis","trajeron"],
        fut=["traeré","traerás","traerá","traeremos","traeréis","traerán"],
        cond=["traería","traerías","traería","traeríamos","traeríais","traerían"],
        subj_pres=["traiga","traigas","traiga","traigamos","traigáis","traigan"],
        subj_imp=["trajera","trajeras","trajera","trajéramos","trajerais","trajeran"],
        imp_aff=["","trae","traiga","traigamos","traed","traigan"],
        inf="traer", ger="trayendo", pp="traído"),
    "caer": dict(pres=["caigo","caes","cae","caemos","caéis","caen"],
        imperf=["caía","caías","caía","caíamos","caíais","caían"],
        indef=["caí","caíste","cayó","caímos","caísteis","cayeron"],
        fut=["caeré","caerás","caerá","caeremos","caeréis","caerán"],
        cond=["caería","caerías","caería","caeríamos","caeríais","caerían"],
        subj_pres=["caiga","caigas","caiga","caigamos","caigáis","caigan"],
        subj_imp=["cayera","cayeras","cayera","cayéramos","cayerais","cayeran"],
        imp_aff=["","cae","caiga","caigamos","caed","caigan"],
        inf="caer", ger="cayendo", pp="caído"),
    "oír": dict(pres=["oigo","oyes","oye","oímos","oís","oyen"],
        imperf=["oía","oías","oía","oíamos","oíais","oían"],
        indef=["oí","oíste","oyó","oímos","oísteis","oyeron"],
        fut=["oiré","oirás","oirá","oiremos","oiréis","oirán"],
        cond=["oiría","oirías","oiría","oiríamos","oiríais","oirían"],
        subj_pres=["oiga","oigas","oiga","oigamos","oigáis","oigan"],
        subj_imp=["oyera","oyeras","oyera","oyéramos","oyerais","oyeran"],
        imp_aff=["","oye","oiga","oigamos","oíd","oigan"],
        inf="oír", ger="oyendo", pp="oído"),
    "reír": dict(pres=["río","ríes","ríe","reímos","reís","ríen"],
        imperf=["reía","reías","reía","reíamos","reíais","reían"],
        indef=["reí","reíste","rió","reímos","reísteis","rieron"],
        fut=["reiré","reirás","reirá","reiremos","reiréis","reirán"],
        cond=["reiría","reirías","reiría","reiríamos","reiríais","reirían"],
        subj_pres=["ría","rías","ría","riamos","riáis","rían"],
        subj_imp=["riera","rieras","riera","riéramos","rierais","rieran"],
        imp_aff=["","ríe","ría","riamos","reíd","rían"],
        inf="reír", ger="riendo", pp="reído"),
    "salir": dict(pres=["salgo","sales","sale","salimos","salís","salen"],
        imperf=["salía","salías","salía","salíamos","salíais","salían"],
        indef=["salí","saliste","salió","salimos","salisteis","salieron"],
        fut=["saldré","saldrás","saldrá","saldremos","saldréis","saldrán"],
        cond=["saldría","saldrías","saldría","saldríamos","saldríais","saldrían"],
        subj_pres=["salga","salgas","salga","salgamos","salgáis","salgan"],
        subj_imp=["saliera","salieras","saliera","saliéramos","salierais","salieran"],
        imp_aff=["","sal","salga","salgamos","salid","salgan"],
        inf="salir", ger="saliendo", pp="salido"),
    "valer": dict(pres=["valgo","vales","vale","valemos","valéis","valen"],
        imperf=["valía","valías","valía","valíamos","valíais","valían"],
        indef=["valí","valiste","valió","valimos","valisteis","valieron"],
        fut=["valdré","valdrás","valdrá","valdremos","valdréis","valdrán"],
        cond=["valdría","valdrías","valdría","valdríamos","valdríais","valdrían"],
        subj_pres=["valga","valgas","valga","valgamos","valgáis","valgan"],
        subj_imp=["valiera","valieras","valiera","valiéramos","valierais","valieran"],
        imp_aff=["","val","valga","valgamos","valed","valgan"],
        inf="valer", ger="valiendo", pp="valido"),
    "caber": dict(pres=["quepo","cabes","cabe","cabemos","cabéis","caben"],
        imperf=["cabía","cabías","cabía","cabíamos","cabíais","cabían"],
        indef=["cupe","cupiste","cupo","cupimos","cupisteis","cupieron"],
        fut=["cabré","cabrás","cabrá","cabremos","cabréis","cabrán"],
        cond=["cabría","cabrías","cabría","cabríamos","cabríais","cabrían"],
        subj_pres=["quepa","quepas","quepa","quepamos","quepáis","quepan"],
        subj_imp=["cupiera","cupieras","cupiera","cupiéramos","cupierais","cupieran"],
        imp_aff=["","cabe","quepa","quepamos","cabed","quepan"],
        inf="caber", ger="cabiendo", pp="cabido"),
    "andar": dict(pres=["ando","andas","anda","andamos","andáis","andan"],
        imperf=["andaba","andabas","andaba","andábamos","andabais","andaban"],
        indef=["anduve","anduviste","anduvo","anduvimos","anduvisteis","anduvieron"],
        fut=["andaré","andarás","andará","andaremos","andaréis","andarán"],
        cond=["andaría","andarías","andaría","andaríamos","andaríais","andarían"],
        subj_pres=["ande","andes","ande","andemos","andéis","anden"],
        subj_imp=["anduviera","anduvieras","anduviera","anduviéramos","anduvierais","anduvieran"],
        imp_aff=["","anda","ande","andemos","andad","anden"],
        inf="andar", ger="andando", pp="andado"),
}

# ---------------------------------------------------------------------------
# VERBOS: [infinitivo, 中文, change, pp_override, base_model, prefix]
# ---------------------------------------------------------------------------
def V(i, c, ch="", pp="", b="", x=""):
    return [i, c, ch, pp, b, x]

VERBS = []
def add(*vs):
    for v in vs:
        VERBS.append(v)

# --- modelos irregulares base ---
add(V("haber","有/助动词",b="haber"), V("tener","有/持有",b="tener"),
    V("venir","来",b="venir"), V("decir","说",b="decir"), V("hacer","做",b="hacer"),
    V("poner","放/放置",b="poner"), V("querer","想/爱",b="querer"), V("saber","知道",b="saber"),
    V("poder","能够",b="poder"), V("dar","给",b="dar"), V("ver","看",b="ver"),
    V("ir","去",b="ir"), V("ser","是",b="ser"), V("estar","在/处于",b="estar"),
    V("traer","带来",b="traer"), V("caer","落下",b="caer"), V("oír","听见",b="oír"),
    V("reír","笑",b="reír"), V("salir","出去",b="salir"), V("valer","值得",b="valer"),
    V("caber","装得下",b="caber"), V("andar","行走",b="andar"))

# --- derivados con prefijo ---
add(V("obtener","获得",b="tener",x="ob"), V("detener","阻止/拘留",b="tener",x="de"),
    V("contener","包含",b="tener",x="con"), V("entretener","娱乐",b="tener",x="entre"),
    V("mantener","保持",b="tener",x="mant"), V("retener","保留",b="tener",x="re"),
    V("sostener","支撑",b="tener",x="sos"),
    V("convenir","适合",b="venir",x="con"), V("devenir","成为",b="venir",x="de"),
    V("prevenir","预防",b="venir",x="pre"), V("provenir","来自",b="venir",x="pro"),
    V("intervenir","干预",b="venir",x="inter"), V("sobrevenir","突然发生",b="venir",x="sobre"),
    V("bendecir","祝福",pp="bendito",b="decir"), V("maldecir","诅咒",pp="maldito",b="decir"),
    V("predecir","预言",b="decir"), V("contradecir","反驳",b="decir"), V("desdecir","反悔",b="decir"),
    V("deshacer","撤销/拆除",b="hacer",x="des"), V("rehacer","重做",b="hacer",x="re"),
    V("componer","组成/修理",b="poner",x="com"), V("disponer","安排/处置",b="poner",x="dis"),
    V("exponer","陈列/阐述",b="poner",x="ex"), V("imponer","强加",b="poner",x="im"),
    V("oponer","反对",b="poner",x="op"), V("proponer","提议",b="poner",x="pro"),
    V("suponer","假设",b="poner",x="sup"), V("sobreponer","克服",b="poner",x="sobre"),
    V("descomponer","分解",b="poner",x="descom"), V("recomponer","重组",b="poner",x="recom"),
    V("presuponer","预设",b="poner",x="presu"),
    V("abstraer","抽象",b="traer",x="abs"), V("atraer","吸引",b="traer",x="atr"),
    V("contraer","收缩/感染",b="traer",x="contr"), V("distraer","使分心",b="traer",x="dis"),
    V("extraer","提取",b="traer",x="extr"), V("retraer","退缩",b="traer",x="retr"),
    V("sustraer","减去",b="traer",x="sustr"),
    V("recaer","复发",b="caer",x="re"),
    V("sonreír","微笑",b="reír",x="son"), V("freír","煎炸",pp="frito",b="reír",x="f"))

# --- regulares -ar ---
add(*[V(w[0], w[1]) for w in [
    ("hablar","说话"),("amar","爱"),("cantar","唱歌"),("bailar","跳舞"),("trabajar","工作"),
    ("estudiar","学习"),("comprar","购买"),("caminar","步行"),("mirar","看"),("escuchar","听"),
    ("llamar","叫/打电话"),("preguntar","提问"),("contestar","回答"),("ayudar","帮助"),("llevar","携带/穿"),
    ("usar","使用"),("necesitar","需要"),("esperar","等待/希望"),("buscar","寻找"),("tocar","触摸/演奏"),
    ("sacar","取出"),("pagar","支付"),("llegar","到达"),("cargar","装载"),("nadar","游泳"),
    ("viajar","旅行"),("cocinar","做饭"),("enseñar","教"),("cenar","吃晚饭"),("desayunar","吃早饭"),
    ("alquilar","租借"),("visitar","参观"),("terminar","结束"),("preparar","准备"),("celebrar","庆祝"),
    ("llorar","哭泣"),("cazar","打猎"),("ganar","赢/赚"),("guardar","保存"),("lavar","洗"),
    ("mandar","命令/寄送"),("montar","骑/安装"),("pasar","经过/度过"),("plantar","种植"),("saltar","跳跃"),
    ("tomar","拿/喝"),("tratar","对待/处理"),("acompañar","陪伴"),("alegrar","使高兴"),("bajar","下降"),
    ("besar","亲吻"),("borrar","擦除"),("brillar","闪耀"),("cambiar","改变"),("charlar","聊天"),
    ("clavar","钉住"),("comentar","评论"),("cortar","切割"),("crear","创造"),("cultivar","耕种"),
    ("dejar","留下/允许"),("dibujar","画画"),("empujar","推"),("entrar","进入"),("enviar","发送"),
    ("explicar","解释"),("firmar","签名"),("flotar","漂浮"),("formar","形成"),("funcionar","运转"),
    ("gastar","花费"),("gritar","喊叫"),("habitar","居住"),("ignorar","忽视"),("intentar","试图"),
    ("inventar","发明"),("limitar","限制"),("llenar","填满"),("luchar","斗争"),("marcar","标记"),
    ("mejorar","改善"),("mezclar","混合"),("narrar","讲述"),("notar","注意到"),("ocupar","占据"),
    ("olvidar","忘记"),("operar","操作/手术"),("parar","停止"),("peinar","梳头"),("poblar","居住/殖民"),
    ("quemar","燃烧"),("rezar","祈祷"),("rotar","旋转"),("separar","分开"),("soplar","吹"),
    ("sudar","出汗"),("tardar","花费时间"),("tirar","扔"),("transportar","运输"),
    ("vagar","游荡"),("vendar","包扎"),("abrazar","拥抱"),("alcanzar","达到/赶上"),("amenazar","威胁"),
    ("analizar","分析"),("aterrizar","着陆"),("avanzar","前进"),("cruzar","穿越"),("destrozar","毁坏"),
    ("finalizar","完成"),("gozar","享受"),("lanzar","投掷"),("organizar","组织"),
    ("realizar","实现"),("rechazar","拒绝"),("rozar","擦过"),("utilizar","利用"),("vacunar","接种"),
    ("valorar","评价"),("acercar","靠近"),("agitar","摇动"),("alabar","赞美"),("amarrar","系牢"),
    ("animar","鼓励"),("anotar","记录"),("apagar","熄灭"),("arreglar","修理"),("asustar","惊吓"),
    ("atar","捆绑"),("atrapar","抓住"),("avisar","通知"),("barajar","洗牌"),("bloquear","封锁"),
    ("bordar","刺绣"),("brotar","发芽"),("bucear","潜水"),("cabalgar","骑马"),("callar","沉默"),
    ("calmar","使平静"),("cansar","使劳累"),("captar","捕捉"),("comparar","比较"),("confiar","信任"),
    ("continuar","继续"),("chocar","碰撞"),("desviar","使偏离"),("editar","编辑"),("encantar","使喜爱"),
    ("ensayar","排练"),("estrenar","首次使用"),("examinar","检查"),("excavar","挖掘"),("extrañar","使惊讶"),
    ("fabricar","制造"),("facilitar","促进"),("felicitar","祝贺"),("frenar","刹车"),("graduar","毕业"),
    ("imaginar","想象"),("importar","重要"),("impulsar","推动"),("indicar","指示"),("inflar","充气"),
    ("informar","通知"),("iniciar","开始"),("insultar","侮辱"),("invitar","邀请"),("irritar","激怒"),
    ("jurar","发誓"),("justificar","证明"),("labrar","耕作"),("lastimar","伤害"),("localizar","定位"),
    ("madrugar","早起"),("manejar","驾驶"),("manipular","操纵"),("marchar","行进"),("mencionar","提及"),
    ("modificar","修改"),("mojar","弄湿"),("molestar","打扰"),("multiplicar","相乘"),("murmurar","低语"),
    ("navegar","航行"),("normalizar","正常化"),("notificar","通知"),("numerar","编号"),("odiar","憎恨"),
    ("ondular","波动"),("ordenar","命令/整理"),("originar","产生"),("oscilar","摆动"),("pactar","约定"),
    ("palpar","触摸"),("pausar","暂停"),("pecar","犯罪"),("pelar","剥皮"),("penalizar","处罚"),
    ("picar","刺/啄"),("pisar","踩"),("planchar","熨烫"),("plasmar","塑造"),("premiar","奖励"),
    ("provocar","挑衅"),("publicar","出版"),("puntuar","打分"),("purificar","净化"),("quitar","去掉"),
    ("radiar","辐射"),("raspar","刮"),("rayar","划线"),("reaccionar","反应"),("rebajar","降低"),
    ("rebotar","反弹"),("recortar","裁剪"),("redactar","撰写"),("reformar","改革"),("regatear","讨价还价"),
    ("registrar","登记"),("regular","调节"),("relacionar","联系"),("rematar","终结"),("repasar","复习"),
    ("resbalar","滑倒"),("resignar","放弃"),("respetar","尊重"),("restar","减去"),("retar","挑战"),
    ("retirar","撤退"),("revelar","揭示"),("revisar","检查"),("rodear","环绕"),("saborear","品尝"),
    ("salar","加盐"),("salpicar","溅"),("sanar","治愈"),("secar","弄干"),("señalar","指出"),
    ("silbar","吹口哨"),("simbolizar","象征"),("subrayar","下划线"),("suspirar","叹气"),("tabular","制表"),
    ("tachar","划掉"),("talar","砍伐"),("tantear","试探"),("tatuar","纹身"),("templar","使缓和"),
    ("titubear","犹豫"),("topar","碰撞"),("totalizar","总计"),("trabar","阻碍"),("traccionar","牵引"),
    ("tragar","吞咽"),("transformar","转变"),("transitar","通行"),("trasladar","迁移"),("truncar","截断"),
    ("tumbar","推倒"),("unificar","统一"),("urbanizar","城市化"),("vaciar","清空"),("validar","验证"),
    ("variar","变化"),("vedar","禁止"),("velar","守护"),("vetar","否决"),("vigilar","监视"),
    ("vocalizar","发声"),("votar","投票"),("zanjar","解决"),("zarpar","起航"),("zozobrar","倾覆"),
    ("zumbar","嗡嗡响"),
]])

# --- -ar con cambio de raíz ---
add(*[V(w[0], w[1], w[2]) for w in [
    ("pensar","思考","e>ie"),("cerrar","关闭","e>ie"),("recomendar","推荐","e>ie"),
    ("comenzar","开始","e>ie"),("empezar","开始","e>ie"),("despertar","唤醒","e>ie"),
    ("sentar","使坐下","e>ie"),("regar","浇灌","e>ie"),("negar","否认","e>ie"),
    ("manifestar","表明","e>ie"),("confesar","承认","e>ie"),("atravesar","穿过","e>ie"),
    ("mentar","提及","e>ie"),("sosegar","平息","e>ie"),("tropezar","绊倒","e>ie"),
    ("tentar","试探","e>ie"),("quebrar","折断","e>ie"),("gobernar","统治","e>ie"),
    ("enterrar","埋葬","e>ie"),("apretar","压紧","e>ie"),("helar","结冰","e>ie"),
    ("alentar","鼓励","e>ie"),("calentar","加热","e>ie"),("cegar","使失明","e>ie"),
    ("concertar","约定","e>ie"),("desterrar","流放","e>ie"),("fregar","擦洗","e>ie"),
    ("reventar","爆裂","e>ie"),("forzar","强迫","o>ue"),("temblar","颤抖","e>ie"),
    ("contar","数/讲述","o>ue"),("mostrar","展示","o>ue"),("encontrar","找到","o>ue"),
    ("recordar","记得","o>ue"),("volar","飞","o>ue"),("sonar","响","o>ue"),
    ("probar","尝试/品尝","o>ue"),("demostrar","证明","o>ue"),("acordar","同意","o>ue"),
    ("soltar","松开","o>ue"),("aprobar","批准","o>ue"),("renovar","更新","o>ue"),
    ("almorzar","吃午饭","o>ue"),("volcar","翻倒","o>ue"),("rodar","滚动","o>ue"),
    ("tostar","烘烤","o>ue"),("soldar","焊接","o>ue"),("rogar","恳求","o>ue"),
    ("acostar","使躺下","o>ue"),("colgar","悬挂","o>ue"),("costar","花费","o>ue"),
    ("trocar","交换","o>ue"),("resonar","回响","o>ue"),("soñar","做梦","o>ue"),
    ("jugar","玩","u>ue"),
]])

# --- regulares -er ---
add(*[V(w[0], w[1], w[2] if len(w)>2 else "", w[3] if len(w)>3 else "") for w in [
    ("comer","吃"),("beber","喝"),("correr","跑"),("vender","卖"),("aprender","学习"),
    ("comprender","理解"),("deber","应该/欠"),("temer","害怕"),("meter","放入"),("barrer","扫地"),
    ("coser","缝纫"),("cometer","犯(错)"),("depender","依赖"),("emprender","着手"),("responder","回答"),
    ("sorprender","使惊讶"),("suceder","发生"),("prometer","承诺"),("prender","点燃/抓住"),("absorber","吸收"),
    ("tejer","编织"),("esconder","隐藏"),("romper","打破","","roto"),("atrever","敢于"),("ofender","冒犯"),
    ("aprehender","逮捕"),
]])

# --- -er con cambio / especiales ---
add(*[V(w[0], w[1], w[2], w[3] if len(w)>3 else "") for w in [
    ("leer","阅读","y"),("creer","相信","y"),("poseer","拥有","y"),
    ("encender","点燃","e>ie"),("atender","照料","e>ie"),("entender","理解","e>ie"),
    ("extender","延伸","e>ie"),("tender","展开","e>ie"),("perder","失去","e>ie"),
    ("verter","倾倒","e>ie"),("ascender","上升","e>ie"),("descender","下降","e>ie"),
    ("cerner","筛","e>ie"),("hender","劈开","e>ie"),("defender","保卫","e>ie"),
    ("morder","咬","o>ue"),("moler","磨碎","o>ue"),("soler","惯常","o>ue"),
    ("doler","疼痛","o>ue"),("mover","移动","o>ue"),("volver","回来","o>ue","vuelto"),
    ("devolver","归还","o>ue","devuelto"),("resolver","解决","o>ue","resuelto"),
    ("disolver","溶解","o>ue","disuelto"),("envolver","包裹","o>ue","envuelto"),
    ("revolver","搅动","o>ue","revuelto"),
]])

# --- -ger / -cer (-er) ---
add(*[V(w[0], w[1]) for w in [
    ("coger","抓/拿"),("escoger","挑选"),("recoger","收集/接"),("proteger","保护"),
    ("acoger","接纳"),("encoger","缩小"),("vencer","战胜"),("convencer","说服"),
    ("conocer","认识"),("aparecer","出现"),("crecer","生长"),("desaparecer","消失"),
    ("merecer","值得"),("nacer","出生"),("obedecer","服从"),("ofrecer","提供"),
    ("pertenecer","属于"),("reconocer","认出"),("establecer","建立"),("florecer","开花"),
    ("agradecer","感谢"),("amanecer","天亮"),("anochecer","天黑"),("carecer","缺乏"),
    ("favorecer","有利于"),("fallecer","去世"),("guarecer","躲避"),("envejecer","变老"),
    ("enriquecer","致富"),("padecer","遭受"),("perecer","灭亡"),("renacer","重生"),
    ("restablecer","恢复"),("complacer","使满意"),("abastecer","供应"),("acontecer","发生"),
    ("apetecer","渴望"),("compadecer","同情"),("convalecer","康复"),("embellecer","美化"),
    ("enfurecer","激怒"),("engrandecer","扩大"),("enloquecer","发疯"),("enrojecer","脸红"),
    ("entristecer","使悲伤"),("estremecer","震动"),("humedecer","弄湿"),("oscurecer","变暗"),
    ("palidecer","变苍白"),("parecer","似乎"),("permanecer","停留"),("placer","使高兴"),
    ("reaparecer","重新出现"),("rejuvenecer","使年轻"),("adolecer","患病"),("atardecer","傍晚"),
    ("encanecer","变白"),("entumecer","麻木"),
]])

# --- regulares -ir ---
add(*[V(w[0], w[1], w[2] if len(w)>2 else "", w[3] if len(w)>3 else "") for w in [
    ("vivir","生活"),("abrir","打开","","abierto"),("escribir","写","","escrito"),("recibir","接收"),("permitir","允许"),
    ("subir","上升"),("decidir","决定"),("descubrir","发现","","descubierto"),("cubrir","覆盖","","cubierto"),("imprimir","打印","","impreso"),
    ("añadir","添加"),("cumplir","履行"),("definir","定义"),("repartir","分发"),("unir","联合"),
    ("dividir","分割"),("prohibir","禁止"),("admitir","承认"),("omitir","省略"),("emitir","发出"),
    ("transmitir","传输"),("persistir","坚持"),("resistir","抵抗"),("existir","存在"),("asistir","出席"),
    ("consistir","在于"),("insistir","坚持"),("sufrir","遭受"),("distinguir","区分"),("extinguir","熄灭"),
    ("delinquir","违法"),("crujir","吱嘎作响"),("bullir","沸腾"),("bruñir","磨光"),("esculpir","雕刻"),
    ("fundir","熔化"),("partir","离开/分成"),("surgir","出现"),("rugir","咆哮"),("mugir","哞叫"),("afligir","使痛苦"),
    ("esparcir","撒"),
    ("hervir","沸腾","e>ie"),("sentir","感觉","e>ie"),("mentir","撒谎","e>ie"),
    ("preferir","更喜欢","e>ie"),("herir","伤害","e>ie"),("consentir","同意","e>ie"),
    ("divertir","使娱乐","e>ie"),("convertir","转变","e>ie"),("advertir","警告","e>ie"),
    ("requerir","要求","e>ie"),("presentir","预感","e>ie"),("disentir","不同意","e>ie"),
    ("asentir","同意","e>ie"),("sugerir","暗示","e>ie"),("inferir","推断","e>ie"),
    ("transferir","转移","e>ie"),("referir","提及","e>ie"),("diferir","延迟","e>ie"),
    ("conferir","授予","e>ie"),
    ("pedir","请求","e>i"),("servir","服务","e>i"),("seguir","跟随","e>i"),
    ("conseguir","获得","e>i"),("perseguir","追逐","e>i"),("proseguir","继续","e>i"),
    ("impedir","阻止","e>i"),("medir","测量","e>i"),("competir","竞争","e>i"),
    ("repetir","重复","e>i"),("despedir","告别/解雇","e>i"),("expedir","签发","e>i"),
    ("vestir","穿衣","e>i"),("elegir","选择","e>i"),("corregir","纠正","e>i"),
    ("regir","统治","e>i"),("gemir","呻吟","e>i"),("rendir","征服","e>i"),
    ("ceñir","束紧","e>i"),("reñir","争吵","e>i"),("teñir","染色","e>i"),
    ("dormir","睡觉","o>ue"),("morir","死亡","o>ue","muerto"),
    ("dirigir","指导"),("exigir","要求"),("fingir","假装"),("sumergir","淹没"),("urgir","紧急"),
    ("lucir","发亮"),("relucir","闪耀"),("zurcir","缝补"),
    ("construir","建造","uir"),("huir","逃跑","uir"),("incluir","包括","uir"),
    ("destruir","摧毁","uir"),("concluir","结束","uir"),("excluir","排除","uir"),
    ("recluir","禁闭","uir"),("atribuir","归因","uir"),("contribuir","贡献","uir"),
    ("distribuir","分配","uir"),("sustituir","替代","uir"),("fluir","流动","uir"),
    ("conducir","驾驶/引导"),("producir","生产"),("reducir","减少"),("traducir","翻译"),
    ("deducir","推断"),("introducir","引入"),("inducir","诱导"),("reproducir","复制"),
]])

# deduplicar por infinitivo (conservar el primero)
seen = set(); FINAL = []
for v in VERBS:
    if v[0] in seen:
        continue
    seen.add(v[0]); FINAL.append(v)
VERBS = FINAL

# prefix = infinitivo - base (automático), con validación
for v in VERBS:
    if v[4]:
        pre = v[0][:-len(v[4])]
        if pre + v[4] != v[0]:
            print("⚠️ PREFIX MISMATCH:", v[0], "base:", v[4], "pre:", pre)
        v[5] = pre
    else:
        v[5] = ""

print("Total verbos únicos:", len(VERBS))

# ---------------------------------------------------------------------------
# MOTOR DE CONJUGACIÓN (JS)
# ---------------------------------------------------------------------------
ENGINE_JS = r"""
// ===== Motor de conjugación español =====
var PRON=["yo","tú","él/ella/usted","nosotros","vosotros","ellos/ellas/ustedes"];
var VOWELS="aeiouáéíóúü";
var END={
 'ar':{pres:['o','as','a','amos','áis','an'],imperf:['aba','abas','aba','ábamos','abais','aban'],indef:['é','aste','ó','amos','asteis','aron'],fut:['é','ás','á','emos','éis','án'],cond:['ía','ías','ía','íamos','íais','ían'],subj_pres:['e','es','e','emos','éis','en']},
 'er':{pres:['o','es','e','emos','éis','en'],imperf:['ía','ías','ía','íamos','íais','ían'],indef:['í','iste','ió','imos','isteis','ieron'],fut:['é','ás','á','emos','éis','án'],cond:['ía','ías','ía','íamos','íais','ían'],subj_pres:['a','as','a','amos','áis','an']},
 'ir':{pres:['o','es','e','imos','ís','en'],imperf:['ía','ías','ía','íamos','íais','ían'],indef:['í','iste','ió','imos','isteis','ieron'],fut:['é','ás','á','emos','éis','án'],cond:['ía','ías','ía','íamos','íais','ían'],subj_pres:['a','as','a','amos','áis','an']}
};
function r1(s,from,to){var i=s.lastIndexOf(from);return i<0?s:s.slice(0,i)+to+s.slice(i+from.length);}
function vowelBeforeC(inf){return inf.length>=4&&VOWELS.indexOf(inf.charAt(inf.length-4))>=0;}
function ends(inf,suf){return inf.slice(-suf.length)===suf;}
function isArr(x){return Object.prototype.toString.call(x)==='[object Array]';}

function stemFor(change,type,mood,idx,stem){
  if(change==='e>ie'||change==='o>ue'||change==='e>i'||change==='u>ue'){
    var chg=false;
    if(change==='e>ie'){
      if(mood==='ind')chg=(idx===0||idx===1||idx===2||idx===5);
      else if(mood==='subj'){if(type==='ir')return(idx===3||idx===4)?r1(stem,'e','i'):r1(stem,'e','ie');chg=(idx===0||idx===1||idx===2||idx===5);}
      else if(mood==='imp')chg=(idx===1||idx===2||idx===5);
    }else if(change==='o>ue'){
      if(mood==='ind')chg=(idx===0||idx===1||idx===2||idx===5);
      else if(mood==='subj'){if(type==='ir')return(idx===3||idx===4)?r1(stem,'o','u'):r1(stem,'o','ue');chg=(idx===0||idx===1||idx===2||idx===5);}
      else if(mood==='imp')chg=(idx===1||idx===2||idx===5);
    }else if(change==='e>i'){
      if(mood==='ind')chg=(idx===0||idx===1||idx===2||idx===5);
      else if(mood==='subj')chg=true;
      else if(mood==='imp')chg=(idx===1||idx===2||idx===5);
    }else if(change==='u>ue'){
      if(mood==='ind')chg=(idx===0||idx===1||idx===2||idx===5);
      else if(mood==='subj')chg=(idx===0||idx===1||idx===2||idx===5);
      else if(mood==='imp')chg=(idx===1||idx===2||idx===5);
    }
    if(!chg)return stem;
    if(change==='e>ie')return r1(stem,'e','ie');
    if(change==='o>ue')return r1(stem,'o','ue');
    if(change==='e>i')return r1(stem,'e','i');
    if(change==='u>ue')return r1(stem,'u','ue');
  }
  return stem;
}

function fixSpelling(inf,form,tense,person){
  if(tense==='subj_pres'){
    if(ends(inf,'gar'))form=form.replace(/g([eé])/g,'gu$1');
    if(ends(inf,'car'))form=form.replace(/c([eé])/g,'qu$1');
    if(ends(inf,'zar'))form=form.replace(/z([eé])/g,'c$1');
    if(ends(inf,'ger')||ends(inf,'gir'))form=form.replace(/g([aá])/g,'j$1');
    if(ends(inf,'guir'))form=form.replace(/gu([aá])/g,'g$1');
    if(ends(inf,'quir'))form=form.replace(/qu([aá])/g,'c$1');
    if(ends(inf,'cer')||ends(inf,'cir')){if(vowelBeforeC(inf))form=form.replace(/c([aá])/g,'zc$1');else form=form.replace(/c([aá])/g,'z$1');}
  }else if(tense==='pres'&&person===0){
    if(ends(inf,'ger')||ends(inf,'gir'))form=form.replace(/g(o)$/,'j$1');
    if(ends(inf,'guir'))form=form.replace(/gu(o)$/,'g$1');
    if(ends(inf,'quir'))form=form.replace(/qu(o)$/,'c$1');
    if(ends(inf,'cer')||ends(inf,'cir')){if(vowelBeforeC(inf))form=form.replace(/c(o)$/,'zc$1');else form=form.replace(/c(o)$/,'z$1');}
  }else if(tense==='indef'&&person===0){
    if(ends(inf,'gar'))form=form.replace(/g([eé])/g,'gu$1');
    if(ends(inf,'car'))form=form.replace(/c([eé])/g,'qu$1');
    if(ends(inf,'zar'))form=form.replace(/z([eé])/g,'c$1');
  }
  return form;
}

function buildPres(v){
  var t=v.type,ch=v.ch,stem=v.stem,out=[];
  for(var i=0;i<6;i++){
    var form;
    if(ch==='uir'){form=stem+(['yo','yes','ye','imos','ís','yen'][i]);}
    else{var s=stemFor(ch,t,'ind',i,stem);form=s+END[t].pres[i];}
    out.push(fixSpelling(v.i,form,'pres',i));
  }
  return out;
}
function buildSubjPres(v){
  var t=v.type,ch=v.ch,stem=v.stem,out=[];
  for(var i=0;i<6;i++){
    var form;
    if(ch==='uir'){form=stem+(i===1?'yas':(i===3?'yamos':(i===4?'yáis':(i===5?'yan':'ya'))));}
    else{var s=stemFor(ch,t,'subj',i,stem);form=s+END[t].subj_pres[i];}
    out.push(fixSpelling(v.i,form,'subj_pres',i));
  }
  return out;
}
function buildIndef(v){
  var t=v.type,ch=v.ch,stem=v.stem,inf=v.i;
  if(ch==='y'){var bs=inf.slice(0,-2);return[bs+'í',bs+'íste',bs+'yó',bs+'ímos',bs+'ísteis',bs+'yeron'];}
  if(ch==='uir'){return[stem+'í',stem+'iste',stem+'yó',stem+'imos',stem+'isteis',stem+'yeron'];}
  if(ends(inf,'ducir')){var rt=inf.slice(0,-5);return[rt+'duje',rt+'dujiste',rt+'dujo',rt+'dujimos',rt+'dujisteis',rt+'dujeron'];}
  var E=END[t].indef,out=[];
  for(var i=0;i<6;i++){
    var s=stem;
    if(t==='ir'&&(ch==='e>ie'||ch==='e>i'||ch==='o>ue')&&(i===2||i===5)){
      s=(ch==='o>ue')?r1(stem,'o','u'):r1(stem,'e','i');
    }
    out.push(fixSpelling(inf,s+E[i],'indef',i));
  }
  return out;
}
function buildSubjImperf(v,indef){
  var s3=indef[5],stem3,ends3;
  if(/(yeron|jeron)$/.test(s3)){stem3=s3.slice(0,-4);ends3=['era','eras','era','éramos','erais','eran'];}
  else if(/ieron$/.test(s3)){stem3=s3.slice(0,-5);ends3=['iera','ieras','iera','iéramos','ierais','ieran'];}
  else{stem3=s3.slice(0,-4);ends3=['ara','aras','ara','áramos','arais','aran'];}
  return ends3.map(function(x){return stem3+x;});
}
function isIrregCond(f){var i=f.indexOf('ría');if(i<0)return false;return VOWELS.indexOf(f.charAt(i-1))<0;}
function deriveSubjFut(cond){
  return cond.map(function(f){
    if(isIrregCond(f)){
      return f.replace('ríamos','riéramos').replace('ríais','riereis').replace('rían','rieran').replace('rías','rieres').replace('ría','riere');
    }else{
      return f.replace('íamos','áremos').replace('íais','areis').replace('ían','aren').replace('ías','ares').replace('ía','are');
    }
  });
}
function buildImpAff(v,pres,subj){
  var t=v.type,ch=v.ch,stem=v.stem,vos;
  if(ch==='uir')vos=stem+'id';
  else vos=stem+(t==='ar'?'ad':(t==='er'?'ed':'id'));
  return ['',pres[2],subj[2],subj[3],vos,subj[5]];
}
function gerPP(v){
  var t=v.type,ch=v.ch,stem=v.stem,ger,pp;
  if(ch==='uir'){ger=stem+'yendo';pp=stem+'ido';}
  else if(ch==='y'){ger=stem+'yendo';pp=stem+'ído';}
  else if(t==='ar'){ger=stem+'ando';pp=stem+'ado';}
  else{
    var gs=stem;
    if(t==='ir'&&(ch==='e>i'||ch==='o>ue'||ch==='e>ie')){gs=(ch==='o>ue')?r1(stem,'o','u'):r1(stem,'e','i');}
    ger=gs+'iendo';pp=stem+'ido';
  }
  if(v.p)pp=v.p;
  return{ger:ger,pp:pp};
}
function pre(x,f){return (x&&f)?(f.charAt(0)===x.charAt(x.length-1)?x+f.slice(1):x+f):(x||f);}
function buildFull(v){
  var type=v.i.slice(-2),stem=v.i.slice(0,-2);
  v.type=type;v.stem=stem;
  var base;
  if(v.b){
    var m=MODELS[v.b];base={};
    ['pres','imperf','indef','fut','cond','subj_pres','subj_imp','imp_aff','inf','ger','pp'].forEach(function(k){
      var outK=(k==='subj_imp')?'subj_imperf':k;
      var val=m[k];
      base[outK]=isArr(val)?val.map(function(x){return pre(v.x,x);}):pre(v.x,val);
    });
    base.imp_aff[0]='';
  }else{
    var pres=buildPres(v),subj=buildSubjPres(v),indef=buildIndef(v);
    var imperf=END[type].imperf.map(function(e){return stem+e;});
    var fut=END[type].fut.map(function(e){return v.i+e;});
    var cond=END[type].cond.map(function(e){return v.i+e;});
    var gp=gerPP(v);
    base={pres:pres,imperf:imperf,indef:indef,fut:fut,cond:cond,subj_pres:subj,subj_imperf:buildSubjImperf(v,indef),imp_aff:buildImpAff(v,pres,subj),inf:v.i,ger:gp.ger,pp:gp.pp};
  }
  if(v.p)base.pp=v.p;
  var H=HABER,pp=base.pp;
  return{
    ind_pres:base.pres,
    ind_perf:H.pres.map(function(h){return h+' '+pp;}),
    ind_imperf:base.imperf,
    ind_indef:base.indef,
    ind_plus:H.imperf.map(function(h){return h+' '+pp;}),
    ind_fut:base.fut,
    ind_cond:base.cond,
    subj_pres:base.subj_pres,
    subj_perf:H.subj_pres.map(function(h){return h+' '+pp;}),
    subj_imperf:base.subj_imperf,
    subj_plus:H.subj_imp.map(function(h){return h+' '+pp;}),
    subj_fut:deriveSubjFut(base.cond),
    imp_aff:base.imp_aff,
    imp_neg:['','no '+base.subj_pres[1],'no '+base.subj_pres[2],'no '+base.subj_pres[3],'no '+base.subj_pres[4],'no '+base.subj_pres[5]],
    inf:base.inf,ger:base.ger,pp:base.pp
  };
}
"""

# ---------------------------------------------------------------------------
# Prueba con node
# ---------------------------------------------------------------------------
def run_node_test():
    import json as _j
    testdir = os.path.join(HERE, "_engine_test")
    os.makedirs(testdir, exist_ok=True)
    data_js = "var HABER=" + _j.dumps(HABER, ensure_ascii=False) + ";\nvar MODELS=" + _j.dumps(MODELS, ensure_ascii=False) + ";\nvar VERBS=" + _j.dumps(
        [{"i": v[0], "c": v[1], "ch": v[2], "p": v[3], "b": v[4], "x": v[5]} for v in VERBS], ensure_ascii=False) + ";\n"
    with open(os.path.join(testdir, "engine.js"), "w", encoding="utf-8") as f:
        f.write(data_js + ENGINE_JS)
    test = r"""
const {execSync}=require('child_process');
const fs=require('fs');
const path=require('path');
eval(fs.readFileSync(path.join(__dirname,'engine.js'),'utf8'));
function findVerb(inf){return VERBS.find(function(v){return v.i===inf;});}
function show(inf){
  var v=findVerb(inf);
  if(!v){console.log('NO EXISTE:',inf);return;}
  var c=buildFull(v);
  console.log('=== '+inf+' ('+v.c+') ===');
  console.log('pres:      '+c.ind_pres.join(' | '));
  console.log('imperf:    '+c.ind_imperf.join(' | '));
  console.log('indef:     '+c.ind_indef.join(' | '));
  console.log('fut:       '+c.ind_fut.join(' | '));
  console.log('cond:      '+c.ind_cond.join(' | '));
  console.log('subj pres: '+c.subj_pres.join(' | '));
  console.log('subj imp:  '+c.subj_imperf.join(' | '));
  console.log('imp +:     '+c.imp_aff.join(' | '));
  console.log('imp -:     '+c.imp_neg.join(' | '));
  console.log('ger/pp:    '+c.ger+' / '+c.pp);
  console.log('perf:      '+c.ind_perf[0]+' / plus: '+c.ind_plus[0]+' / subj perf: '+c.subj_perf[1]);
  console.log('');
}
['hablar','comer','vivir','ser','ir','estar','haber','tener','obtener','venir','decir','hacer','poner','poder','querer','saber','dar','ver','traer','caer','oír','reír','salir','pensar','empezar','almorzar','jugar','llegar','sacar','alcanzar','pedir','seguir','dormir','morir','volver','resolver','construir','producir','conocer','vencer','coger','leer','creer','distinguir','delinquir','sentir','hervir','elegir','corregir','freír','tender','mover'].forEach(show);
console.log('TOTAL VERBOS:', VERBS.length);
"""
    with open(os.path.join(testdir, "test.js"), "w", encoding="utf-8") as f:
        f.write(test)
    node = r"C:\Users\迪丽希斯\.workbuddy\binaries\node\versions\22.22.2\node.exe"
    if not os.path.exists(node):
        node = "node"
    r = subprocess.run([node, "test.js"], cwd=testdir, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout)
    if r.returncode != 0:
        print("STDERR:", r.stderr)
        sys.exit(1)
    return testdir

# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def build_html():
    import json as _j
    verbs_data = [{"i": v[0], "c": v[1], "ch": v[2], "p": v[3], "b": v[4], "x": v[5],
                   "ir": 1 if (v[2] or v[3] or v[4] or v[0][-3:] in ("gar","car","zar","ger","gir","cer","cir","uir","guir","quir")) else 0}
                  for v in VERBS]
    data_js = ("var HABER=" + _j.dumps(HABER, ensure_ascii=False, separators=(",", ":")) +
               ";\nvar MODELS=" + _j.dumps(MODELS, ensure_ascii=False, separators=(",", ":")) +
               ";\nvar VERBS=" + _j.dumps(verbs_data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    with open(os.path.join(HERE, "_engine_test", "engine.js"), "r", encoding="utf-8") as f:
        engine = f.read().split("// ===== Motor", 1)[1] if False else ENGINE_JS
    return data_js, engine

testdir = run_node_test()

# ---------------------------------------------------------------------------
# Construir HTML final
# ---------------------------------------------------------------------------
UI_JS = r"""
// ===== Interfaz =====
(function(){
  var listEl=document.getElementById('vlist');
  var idxEl=document.getElementById('idx');
  var searchEl=document.getElementById('search');
  var detailEl=document.getElementById('detail');
  var countEl=document.getElementById('vcount');
  var titleEl=document.getElementById('vtitle');
  var curLetter='', curQuery='', selected=null, cache={};
  var LETTERS='ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'.split('');

  function norm(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
  function verbsFiltered(){
    var q=norm(curQuery);
    return VERBS.filter(function(v){
      if(curLetter && v.i.charAt(0).toUpperCase()!==curLetter) return false;
      if(q){var hay=norm(v.i)+' '+norm(v.c);if(hay.indexOf(q)<0)return false;}
      return true;
    });
  }
  function renderIndex(){
    var present={};
    VERBS.forEach(function(v){present[v.i.charAt(0).toUpperCase()]=1;});
    idxEl.innerHTML=LETTERS.map(function(L){
      return '<button class="idxbtn'+(present[L]?'':' off')+'" data-l="'+L+'">'+L+'</button>';
    }).join('');
  }
  var selEl=null,listTimer=null;
  function itemHtml(v){
    var sel=(selected&&selected.i===v.i)?' sel':'';
    return '<div class="vitem'+sel+'" data-inf="'+v.i+'">'+
      '<span class="vinf">'+v.i+'</span>'+
      '<span class="vcn">'+v.c+'</span>'+
      (v.ir?'<span class="tag irr">不规则</span>':'<span class="tag reg">规则</span>')+
      '</div>';
  }
  function renderList(){
    var vs=verbsFiltered();
    countEl.textContent=vs.length+' / '+VERBS.length+' 个动词';
    if(listTimer){clearTimeout(listTimer);listTimer=null;}
    if(!vs.length){listEl.innerHTML='<div class="empty">没有匹配的动词</div>';selEl=null;return;}
    var CH=150;
    listEl.innerHTML=vs.slice(0,CH).map(itemHtml).join('');
    if(vs.length>CH){
      var i=CH;
      (function step(){
        if(i>=vs.length)return;
        var end=Math.min(i+CH,vs.length);
        var frag=document.createElement('div');
        frag.innerHTML=vs.slice(i,end).map(itemHtml).join('');
        while(frag.firstChild)listEl.appendChild(frag.firstChild);
        i=end;
        listTimer=setTimeout(step,1);
      })();
    }
    selEl=listEl.querySelector('.vitem.sel');
  }
  function tenseLabel(key){
    var m={
      ind_pres:['陈述式现在时','Presente'],
      ind_perf:['现在完成时','Pretérito perfecto'],
      ind_imperf:['过去未完成时','Pretérito imperfecto'],
      ind_indef:['简单过去时','Pretérito indefinido'],
      ind_plus:['过去完成时','Pretérito pluscuamperfecto'],
      ind_fut:['将来时','Futuro simple'],
      ind_cond:['条件式','Condicional simple'],
      subj_pres:['虚拟式现在时','Presente de subjuntivo'],
      subj_perf:['虚拟式现在完成时','Pretérito perfecto de subjuntivo'],
      subj_imperf:['虚拟式过去未完成时','Pretérito imperfecto de subjuntivo'],
      subj_plus:['虚拟式过去完成时','Pretérito pluscuamperfecto de subjuntivo'],
      subj_fut:['虚拟式将来时','Futuro de subjuntivo'],
      imp_aff:['命令式（肯定）','Imperativo afirmativo'],
      imp_neg:['命令式（否定）','Imperativo negativo']
    };
    return m[key]||[key,key];
  }
  function tenseBlock(key,arr){
    var lb=tenseLabel(key);
    var rows=arr.map(function(f,i){
      return '<div class="trow'+(i===0?' yo':'')+'"><span class="tper">'+PRON[i]+'</span><span class="tform">'+f+'</span></div>';
    }).join('');
    return '<div class="tense"><div class="tname"><b>'+lb[0]+'</b><i>'+lb[1]+'</i></div>'+rows+'</div>';
  }
  function moodBlock(color,title,keys){
    var inner='';
    keys.forEach(function(k){inner+=tenseBlock(k,cache[selected.i][k]);});
    return '<section class="mood" style="--mc:'+color+'"><h3 class="mhead">'+title+'</h3><div class="tensegrid">'+inner+'</div></section>';
  }
  function select(inf){
    var v=null;
    VERBS.forEach(function(x){if(x.i===inf)v=x;});
    if(!v)return;
    selected=v;
    if(!cache[inf])cache[inf]=buildFull(JSON.parse(JSON.stringify(v)));
    var c=cache[inf];
    titleEl.innerHTML='<span class="big">'+v.i+'</span><span class="cn">'+v.c+'</span>'+
      (v.ir?'<span class="tag irr">不规则</span>':'<span class="tag reg">规则</span>')+
      '<span class="tag type">-'+v.i.slice(-2)+'</span>';
    var html='';
    html+=moodBlock('#C60B1E','陈述式 Indicativo',['ind_pres','ind_perf','ind_imperf','ind_indef','ind_plus','ind_fut','ind_cond']);
    html+=moodBlock('#1E5AA8','虚拟式 Subjuntivo',['subj_pres','subj_perf','subj_imperf','subj_plus','subj_fut']);
    html+=moodBlock('#8B2500','命令式 Imperativo',['imp_aff','imp_neg']);
    html+='<section class="mood imp"><h3 class="mhead">非人称形式 Formas impersonales</h3><div class="impgrid">'+
      '<div class="impcell"><span class="ilab">原形 Infinitivo</span><b>'+c.inf+'</b></div>'+
      '<div class="impcell"><span class="ilab">副动词 Gerundio</span><b>'+c.ger+'</b></div>'+
      '<div class="impcell"><span class="ilab">过去分词 Participio</span><b>'+c.pp+'</b></div>'+
      '</div></section>';
    detailEl.innerHTML=html;
    if(selEl)selEl.classList.remove('sel');
    selEl=listEl.querySelector('.vitem[data-inf="'+inf+'"]');
    if(selEl)selEl.classList.add('sel');
    detailEl.scrollTop=0;
  }
  idxEl.addEventListener('click',function(e){
    var b=e.target.closest('.idxbtn');
    if(!b||b.classList.contains('off'))return;
    curLetter=(curLetter===b.dataset.l)?'':b.dataset.l;
    idxEl.querySelectorAll('.idxbtn').forEach(function(x){x.classList.toggle('act',x===b&&!!curLetter);});
    renderList();
  });
  searchEl.addEventListener('input',function(){curQuery=searchEl.value;renderList();});
  listEl.addEventListener('click',function(e){
    var el=e.target.closest('.vitem');
    if(el)select(el.getAttribute('data-inf'));
  });
  renderIndex();select('hablar');renderList();
})();
"""

CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
:root{--red:#C60B1E;--gold:#FFC400;--blue:#1E5AA8;--ink:#2b2723;--sub:#8a837a;--bg:#FAF6F0;--card:#ffffff;--line:#e8e0d4;--irr:#FFF8E6}
html,body{background:var(--bg);color:var(--ink);font-family:"Segoe UI","Microsoft YaHei",system-ui,sans-serif}
header{position:sticky;top:0;z-index:50;background:linear-gradient(135deg,#C60B1E,#E0442C);color:#fff;padding:14px 20px;box-shadow:0 2px 10px rgba(0,0,0,.15)}
header h1{font-size:20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
header h1 .flag{letter-spacing:2px}
header .sub{display:flex;align-items:center;gap:10px;margin-top:8px}
header .sub .logo{height:23px;width:23px;border-radius:6px;object-fit:cover;background:#fff;padding:1px;box-shadow:0 1px 4px rgba(0,0,0,.3)}
header .sub .brand{font-size:16px;font-weight:800;letter-spacing:2px;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.3)}
.toprow{display:flex;gap:10px;align-items:center;margin-top:10px;flex-wrap:wrap}
#search{flex:1;min-width:200px;padding:9px 14px;border:none;border-radius:20px;font-size:14px;outline:none}
#vcount{font-size:12px;opacity:.95;white-space:nowrap}
#idx{display:flex;flex-wrap:wrap;gap:5px;margin:12px 20px 0}
.idxbtn{width:34px;height:34px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--ink);font-weight:700;cursor:pointer;font-size:14px}
.idxbtn:hover{background:var(--gold)}
.idxbtn.off{opacity:.3;cursor:default}
.idxbtn.act{background:var(--red);color:#fff;border-color:var(--red)}
.layout{display:grid;grid-template-columns:350px 1fr;gap:16px;padding:16px 20px 40px;align-items:start}
.rcol{min-width:0}
.vpanel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px;max-height:calc(100vh - 170px);overflow:auto;position:sticky;top:150px}
.vitem{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:8px;cursor:pointer;border-bottom:1px dashed #f0e9dd}
.vitem:hover{background:#fff7e6}
.vitem.sel{background:var(--red);color:#fff}
.vitem.sel .vcn{color:#ffe0d6}
.vitem.sel .tag.irr{background:rgba(255,255,255,.25);color:#fff}
.vinf{font-weight:700;font-size:15px}
.vcn{font-size:12px;color:var(--sub);flex:1}
.tag{font-size:10px;padding:2px 7px;border-radius:10px;white-space:nowrap}
.tag.reg{background:#e6f4ea;color:#1e7a3c}
.tag.irr{background:var(--irr);color:#b8860b}
.tag.type{background:#eef2fa;color:var(--blue)}
.empty{padding:30px;text-align:center;color:var(--sub)}
#detail{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;min-height:400px}
#vtitle{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px;padding-bottom:14px;border-bottom:2px solid var(--line)}
#vtitle .big{font-size:30px;font-weight:800;color:var(--red)}
#vtitle .cn{font-size:16px;color:var(--sub)}
.mood{margin-bottom:20px;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.mhead{background:var(--mc);color:#fff;padding:10px 14px;font-size:15px}
.tensegrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;padding:12px}
.tense{background:#fdfbf7;border:1px solid #efe7da;border-radius:10px;padding:8px 10px}
.tname{display:flex;flex-direction:column;margin-bottom:6px;border-bottom:1px dashed #e5dccd;padding-bottom:5px}
.tname b{font-size:12.5px}
.tname i{font-size:11px;color:var(--sub);font-style:normal}
.trow{display:flex;gap:8px;padding:3px 0;font-size:13.5px}
.tper{width:86px;color:var(--sub);font-size:11.5px;padding-top:2px;flex-shrink:0}
.trow.yo .tform{color:var(--red);font-weight:700}
.impgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;padding:12px}
.impcell{background:#fdfbf7;border:1px solid #efe7da;border-radius:10px;padding:12px;text-align:center}
.impcell .ilab{display:block;font-size:11px;color:var(--sub);margin-bottom:4px}
.impcell b{font-size:18px;color:var(--blue)}
@media(max-width:920px){
  .layout{grid-template-columns:1fr}
  .vpanel{position:static;max-height:300px}
  #idx{margin:10px 12px 0}
  .layout{padding:12px}
  header h1{font-size:17px}
}
"""

def main_html():
    import json as _j, base64 as _b64
    def minjs(s):
        return "\n".join(line.strip() for line in s.splitlines() if line.strip())
    _logo_path = os.path.join(HERE, "assets", "logo-piano-small.jpg")
    if os.path.exists(_logo_path):
        with open(_logo_path, "rb") as _f:
            logo_b64 = "data:image/jpeg;base64," + _b64.b64encode(_f.read()).decode("ascii")
    else:
        logo_b64 = ""
    verbs_data = [{"i": v[0], "c": v[1], "ch": v[2], "p": v[3], "b": v[4], "x": v[5],
                   "ir": 1 if (v[2] or v[3] or v[4] or v[0][-3:] in ("gar","car","zar","ger","gir","cer","cir","uir","guir","quir")) else 0}
                  for v in VERBS]
    data_js = ("var HABER=" + _j.dumps(HABER, ensure_ascii=False, separators=(",", ":")) +
               ";\nvar MODELS=" + _j.dumps(MODELS, ensure_ascii=False, separators=(",", ":")) +
               ";\nvar VERBS=" + _j.dumps(verbs_data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>西班牙语动词变位表 · Tabla de Conjugación</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20100%20100'%3E%3Crect%20width='100'%20height='100'%20rx='22'%20fill='%23C60B1E'/%3E%3Ctext%20x='50'%20y='70'%20font-size='54'%20text-anchor='middle'%20fill='%23FFC400'%20font-family='Arial'%20font-weight='bold'%3EES%3C/text%3E%3C/svg%3E">
<style>__CSS__</style>
</head>
<body>
<header>
  <h1><span class="flag">🇪🇸</span> 西班牙语动词变位表 <span class="flag">Tabla de Conjugación</span></h1>
  <div class="sub"><img class="logo" src="__LOGO__" alt="涛子办事处"><span class="brand">涛子办事处</span></div>
  <div class="toprow">
    <input id="search" type="search" placeholder="搜索动词或中文含义…">
    <span id="vcount"></span>
  </div>
</header>
<div id="idx"></div>
<div class="layout">
  <div class="vpanel" id="vlist"></div>
  <div class="rcol">
    <div id="vtitle"></div>
    <div id="detail"><div class="empty">选择左侧动词查看完整变位</div></div>
  </div>
</div>
<script>
__DATA__
__ENGINE__
</script>
<script>
__UI__
</script>
</body>
</html>"""
    html = html.replace("__CSS__", CSS).replace("__DATA__", data_js).replace("__ENGINE__", minjs(ENGINE_JS)).replace("__UI__", minjs(UI_JS)).replace("__LOGO__", logo_b64)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML 写入:", OUT, os.path.getsize(OUT), "bytes")

main_html()


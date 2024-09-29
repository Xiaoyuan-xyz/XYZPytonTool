# 汉字顺位

def jyuni_check(s: str):
    len_s = len(s)
    assert (len_s % 7 == 0)

    twice_list = []
    once_list = []
    # 教凸朝读A二ウ
    toppan_list = []
    asahi_list = []
    web_list = []
    kyouka_list = []

    target_lists = {
        0: kyouka_list,
        1: toppan_list,
        2: asahi_list,
        3: asahi_list,
        4: web_list,
        5: toppan_list,
        6: web_list,
    }

    for i in range(len_s // 7):
        for j in range(7):
            index = i * 7 + j
            kanji = s[index]
            if kanji in twice_list:
                continue
            target_list = target_lists.get(j)
            if kanji in target_list:
                continue
            target_list.append(kanji)
            if s[index] in once_list:
                once_list.remove(s[index])
                twice_list.append(kanji)
            once_list.append(kanji)
    return twice_list


s = "日人日日日国日" \
    "行一年年人人人" \
    "人日大大今大出" \
    "本大人人大年大" \
    "時年国国一地一" \
    "学出会会分日思" \
    "大本本本出本今" \
    "生中中中時中見" \
    "食子者月事生事" \
    "何見一事年政分" \
    "月国出出月会本" \
    "見言月一行一気" \
    "今上時者気民時" \
    "会分事時見化行" \
    "話生学分中業中" \
    "中手上上本的方" \
    "来自生生思世年" \
    "国行分同会自間" \
    "気者長長上立上" \
    "書二子学間代入" \
    "年間東子方法生" \
    "私事手後最動自" \
    "出思自手子戦言" \
    "物時同見前行会" \
    "事気見合言文前" \
    "一会合自生学子" \
    "間十後行入発手" \
    "子家社間新方合" \
    "電女前高自成場" \
    "手三間前手分作" \
    "語前高発的物来" \
    "前的発社無上感" \
    "入方業東私主後" \
    "分入市入合出私" \
    "先小場場来社回" \
    "車地田業場家用" \
    "上合入方円時的" \
    "曜後地内金東最" \
    "家目円今後権目" \
    "買長行市回事動" \
    "金場京対何間月" \
    "料代代新報制何" \
    "休私部的当教当" \
    "思下新部目合定" \
    "校立金円話第下" \
    "聞部目地感者物" \
    "友学対実情経者" \
    "理物立議高治体" \
    "言月内田動定新" \
    "部田回金下後無" \
    "所何政回笑内国" \
    "社来方目作力話" \
    "週彼今明国対発" \
    "新話的定発高食" \
    "字体議代業市部" \
    "強動勝選用産度" \
    "場社選相定子実" \
    "方知定立記界学" \
    "合理実員者条理" \
    "飲山員作食平高" \
    "好内相京社関全" \
    "使同朝政全山地" \
    "自心山力料軍使" \
    "円発北開学活記" \
    "店高約気女場通" \
    "高実戦北楽気楽" \
    "屋作力関長体内" \
    "毎当開体画済業" \
    "名新明決度新性" \
    "山世民性好部書" \
    "教今万連通長家" \
    "明書教理明海品" \
    "下度作小理多味" \
    "作明米教物開様" \
    "後五決取実府変" \
    "読戦体問部明良" \
    "口力小全店争持" \
    "番名表約先下社" \
    "勉金言言良金画" \
    "長性度勝体議力" \
    "道対通最連都先" \
    "漢意連戦不画多" \
    "地用最米家約明" \
    "持男安民期入長" \
    "水主理表内見取" \
    "動通性安味通笑" \
    "小関全山売義知" \
    "京文化家同用心" \
    "駅屋気主開現同" \
    "切感法当近天以" \
    "東郎家化地域近" \
    "意業関県結理対" \
    "仕定問通買道開" \
    "外政話動関和付" \
    "朝持主調書実外" \
    "楽道県法品連金" \
    "業外当保心書成" \
    "度取動話性図意" \
    "母所取要取朝関" \
    "病現保万小三小" \
    "田最野度成原所" \
    "二化現現名進女" \
    "近四下来知北面" \
    "室先点野美前少" \
    "帰民務下所月名" \
    "通身調思以農好" \
    "用不川党対島結" \
    "館口所朝田水報" \
    "住川用受変保情" \
    "女東都務持心数" \
    "十相来制安機真" \
    "味多外用初度不" \
    "体法受強多言考" \
    "画全区外付題立" \
    "院聞世所市外初" \
    "者情制意東資店" \
    "木野氏売外所山" \
    "文考知成様考化" \
    "安向党世数問料" \
    "少平強期株作現" \
    "父成期女予二法" \
    "火軍思記使近続" \
    "便開女文少南買" \
    "問教文校山同代" \
    "着経校持力結仕" \
    "土信成川仕工要" \
    "都近意数利際車" \
    "目以名指意変期" \
    "習語要経真公問" \
    "三面数区資西機" \
    "市連公題万調水" \
    "知問不以相表表" \
    "旅原以書続田市" \
    "回顔経公戦小切" \
    "達正続続現利能" \
    "形機島点法京色" \
    "多九持知代要加" \
    "海次書組番紀売" \
    "願数道不表土電" \
    "花美指都面全安" \
    "発回記首引領戦" \
    "員食首物終安道" \
    "転表多機投性連" \
    "内八物多有正相" \
    "音声題道昨手美" \
    "科水原加水意特" \
    "予報報鮮立集番" \
    "園真千正能形終" \
    "心味正報愛族可" \
    "開界先感考皇着" \
    "待無機原信川活" \
    "町少院名屋以田" \
    "親要初院主名予" \
    "薬海権心選語違" \
    "風変組権価統向" \
    "品結位初切神選" \
    "図切加第要数込" \
    "雨重産先電強強" \
    "定天画元車石屋" \
    "変神品向題章主" \
    "夜記心島決支文" \
    "受木界産第運世" \
    "表集元株着重教" \
    "全和重三集使聞" \
    "午員真利加働読" \
    "止引集品天期東" \
    "族公三設想不受" \
    "乗画向重込料状" \
    "川死男電強米題" \
    "運安木活達設調" \
    "天兵設協化党風" \
    "最親海面聞加達" \
    "色六利位格改次" \
    "真治鮮査在諸正" \
    "急決第和問品解" \
    "号太感画野字利" \
    "空氏判界京由確" \
    "四衛語男機目決" \
    "題強込込勝交愛" \
    "歩使支午朝労経" \
    "北込進支可次保" \
    "男朝村氏活広過" \
    "野受治海週共引" \
    "映島育必平境有" \
    "元解電認道有第" \
    "結市協育員基野" \
    "験期面進位来必" \
    "立様府治産展応" \
    "足村打考式流集" \
    "計活認木調太写" \
    "連頭水切帰王始" \
    "肉題近計色武原" \
    "売万半告他信二" \
    "早組使際特決素" \
    "歌仕投判教野点" \
    "利白考引世院元" \
    "線指活交経戸白" \
    "引説査近駅独他" \
    "活七交件公万身" \
    "送能和集約件重" \
    "半京増水早憲員" \
    "機葉平投始解信" \
    "試第計付違寺公" \
    "伝流団験元思在" \
    "公然信聞二革天" \
    "当初無核読住果" \
    "夏足広打男組送" \
    "紙円藤読別古直" \
    "取在売容保最設" \
    "起門美団向伝帰" \
    "五調核情受命参" \
    "温笑解信張元然" \
    "宿品件府過位海" \
    "終電引能計食語" \
    "正議聞結次在足" \
    "写直験村正球神" \
    "様着得官周半置" \
    "茶保料解確員別" \
    "世別資示口判早" \
    "注夫情資風特張" \
    "以音次使容口流" \
    "約選歳総校葉円" \
    "調元総口友面口" \
    "同権論真原風産" \
    "代特切検三幕朝" \
    "右義結無送向音" \
    "広父術車半州想" \
    "交利直特然易約" \
    "初制官語川県界" \
    "兄続省平我商組" \
    "悪風際私海建待" \
    "洗北必次白環空" \
    "痛石係藤身村週" \
    "昼車館委未相得" \
    "働進予料夜館勝" \
    "付夜付楽文各昨" \
    "銀伝改直点移転" \
    "有母口得得反格" \
    "始加示改類達験" \
    "婚助能談待量彼" \
    "左点共係応史介" \
    "数産始予木取悪" \
    "化務容広花然残" \
    "説件有局果選式" \
    "不命井運直洋配" \
    "古番委価商総常" \
    "酒落車演起受線" \
    "晩付参疑参町指" \
    "寝得反裁神江花" \
    "台半工食落配京" \
    "万戸演論悪情葉" \
    "関好神職足輸川" \
    "飯空職反辺令三" \
    "性有再再界身男" \
    "相違変基休兵供" \
    "医吉応格重女校" \
    "英殺基落語別半" \
    "赤起任変解規夜" \
    "別運特少馬官構" \
    "白置台参彼持落" \
    "特料告二優知検" \
    "保士求増必十歩" \
    "九返局番配造容" \
    "質藤検任和当観" \
    "魚論私住値先商" \
    "記楽科歳登説質" \
    "服際疑始寝協県" \
    "育歳敗有更記更" \
    "夫色死井了鮮等" \
    "重帰球在指報映" \
    "力歩統応常帝限" \
    "集井在半写閣運" \
    "西悪住優都話位" \
    "熱広西神音鉄進" \
    "席店写終北策休" \
    "期反優科是論島" \
    "歳町午果流陸演" \
    "遅形楽求映仏形" \
    "葉百済策久木乗" \
    "八光二確空術示" \
    "現首町美転想試" \
    "主勝少済組係計" \
    "頭必談球個直平" \
    "配土谷共務五台" \
    "留係格省像宗務" \
    "面由提台介求際" \
    "消愛岡転試備起" \
    "工都策置運読制" \
    "式住裁術毎類求" \
    "弟江害配素参認" \
    "実西身別土役像" \
    "七売番止状務民" \
    "的放減工供増友" \
    "遊確運統台計木" \
    "授過億死録置個" \
    "六張説放曜漢態" \
    "難約果過限構基" \
    "介馬営身増路広" \
    "絵状案葉告回説" \
    "降待福西葉企毎" \
    "次古研提死団育" \
    "答想別研演貿顔" \
    "平始費流収害和" \
    "々官病送広清登" \
    "考交止監院護親" \
    "借読監説返真単" \
    "報千転何単得価" \
    "牛米葉害残植段" \
    "練配収敗親観優" \
    "県若企可県今放" \
    "階終価店島点工" \
    "南資食親等氏種" \
    "点常確営額止注" \
    "産果役両歌他止" \
    "春呼展施設式返" \
    "速校医味飲費光" \
    "申武過究構例職" \
    "遠共可供顔裁曲" \
    "両計終式歩果伝" \
    "青残建医注能撮" \
    "冬判割谷置製頭" \
    "議役勢案打育院" \
    "姉城店白件続客" \
    "忘院置試放歴量" \
    "彼他負役検財園" \
    "要総何着議光北" \
    "民術試億載士件" \
    "秋支石病西帯治" \
    "決送税展職器材" \
    "寒族側町販校都" \
    "無両流側米確載" \
    "法乗声伝観衆備" \
    "神団各声役空交" \
    "絡松究佐証船万" \
    "供映放足頭消土" \
    "建応松護曲少飲" \
    "成済士収乗任歌" \
    "局線担岡満城製" \
    "込買残割説初収" \
    "診設韓勢制線増" \
    "座右足士験割紹" \
    "落供護企俺示再" \
    "村格師各願勢温" \
    "士病宮状営四係" \
    "冷打消歩進乱資" \
    "研視親起比絵覚" \
    "千早違良雨台議" \
    "島勢影夫井銀病" \
    "返御夫証皆等効" \
    "焼断送減誰価頂" \
    "原式防督民屋支" \
    "経質伝銀系源念" \
    "暑師映断育味声" \
    "和台着技帯格程" \
    "課党佐導認様駅" \
    "残告状空完指投" \
    "寺深落好係温反" \
    "界存天館夫足録" \
    "菜争白師消習難" \
    "指室移移焼種母" \
    "証覚義写太必普" \
    "百史由税止藤皆" \
    "夕側仕残示満満" \
    "身飛率倍頑何装" \
    "区参補返益認政" \
    "黒可領防種復完" \
    "対態張福区派寝" \
    "鳥営崎映声営習" \
    "役府賞被病福術" \
    "震突読石覚始走" \
    "忙巻起与痛影住" \
    "究容両費為税細" \
    "太姿軍復段河販" \
    "感育施建線白由" \
    "歯之督違去徳存" \
    "違介復様住質久" \
    "荷建断賞園盟型" \
    "閉南授千交挙夫" \
    "由構史視念課古" \
    "覚認風仕居放緒" \
    "去位古松際無遊" \
    "雪達争派再門告" \
    "妹転屋注伝職影" \
    "加左働義反聞願" \
    "客皇導警携藩役" \
    "払宮銀授千差死" \
    "阪守限土士区判" \
    "郵満技領支収消" \
    "押消視由君起周" \
    "信任空限型布例" \
    "必医配崎紹率町" \
    "辞蔵土線末限頃" \
    "昨止味韓由模欲" \
    "係造返担治感値" \
    "声居式昨球電石" \
    "確離命負藤臣非" \
    "港根門介材引断" \
    "他予形乗基降馬" \
    "末路光宮室織士" \
    "洋字倍補越蔵科" \
    "光座州待習積室" \
    "ー工派買率死器" \
    "割寺横常僕存接" \
    "選基阪比歳首太" \
    "談客待質遊色焼" \
    "置急象率緒整側" \
    "鉄船戸値工切速" \
    "祭図若張石応夏" \
    "窓追与備費張苦" \
    "門隊修療母低探" \
    "参査早念谷景系" \
    "顔背算態総比号" \
    "支観質消欲急旅" \
    "短誰殺母細九共" \
    "具黒療想絶占追" \
    "険素個観苦円末" \
    "治息労挙赤接座" \
    "美価橋影編容類" \
    "泳将規殺査律十" \
    "横伊警門質拡打" \
    "組改南光普状望" \
    "備県念象負深館" \
    "続撃様修古林済" \
    "器失好算光宮村" \
    "静泉備額号技展" \
    "単老常難嫌響離" \
    "犬良額武態過我" \
    "米示挙天頃圧字" \
    "失振英毎村印医" \
    "務号昨英夏常提" \
    "費像観風座八飛" \
    "類職援器製助痛" \
    "苦王難早備及赤" \
    "健識差馬科車割" \
    "走警介命超倉管" \
    "貸花想屋局防技" \
    "礼優園阪酒宣識" \
    "暗投音字術細絶" \
    "解英武五減頭図" \
    "飛細歩音氏衛営" \
    "給局器援春象宅" \
    "詞難線追判吉僕" \
    "直種太歌形親曜" \
    "石証注働松美西" \
    "進走態段走両熱" \
    "準念財形急火急" \
    "軽寄字王客極去" \
    "職商愛室難守施" \
    "富青黒州政油頑" \
    "護谷製座提根負" \
    "果害馬太詳付改" \
    "禁奥失横火隊俺" \
    "向派乗型婚与誰" \
    "状僕歌黒南園比" \
    "困佐青戸追六抜" \
    "故頼王差宅花君" \
    "首横域述銀歌局" \
    "誕友十規失楽帯" \
    "資再急製速馬申" \
    "格増族号町韓歳" \
    "然紀例構王禁路" \
    "卒統助十非科移" \
    "案答路軍断側具" \
    "術差室園割可購" \
    "紹火郎域命施団" \
    "堂苦頭然済良護" \
    "容器準族香郎視" \
    "段収森障疲興査" \
    "在段供争券層福" \
    "角異良守旅星居" \
    "察血庁古温融換" \
    "耳護構史企再除" \
    "税紙振評団落雨" \
    "接俺退郎恋験論" \
    "情歌沢児館障象" \
    "丈渡評材幸察命" \
    "船与客個字徴降" \
    "登注姿橋横百造" \
    "防条春柄柄廃戻" \
    "第演江秋求末差" \
    "認算商姿健冷囲" \
    "際赤夜愛程候療" \
    "布備証南沢松編" \
    "森独低急英査黒" \
    "康象秋頭黒失害" \
    "君清競財競紙族" \
    "常技追席四省企" \
    "位州材深量列費" \
    "届申独沢共伊米" \
    "池例被庁準貨沢" \
    "低働訴訪算像振" \
    "観景右船効態区" \
    "曲領守宅掲写低" \
    "王春左答十売未" \
    "細抜望若戻系派" \
    "季遠宅識賞御適" \
    "死橋段退阪究氏" \
    "限源紙響任転撃" \
    "歴芸港望降導修" \
    "節影識労視欧減"



jyuni = jyuni_check(s)
print(''.join(jyuni))
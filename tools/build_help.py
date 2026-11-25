from pathlib import Path
import csv,json,re,sys
OUT=Path(__file__).resolve().parent.parent
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else OUT/'runtime-source'
entries=[]
def add(id,group,en,ar,meaning,meaning_ar,use,use_ar,calc,calc_ar,aliases=(),status='reference'):
    entries.append(dict(id=id,group=group,en=en,ar=ar,meaning={'en':meaning,'ar':meaning_ar},use={'en':use,'ar':use_ar},calculation={'en':calc,'ar':calc_ar},aliases=list(aliases),status=status))
# Strategy ID order exactly from the frozen register; these explanatory summaries are not changes to the definitions.
strategies='''الجاهزية المالية|Check that obligations and protected reserves are covered before market exposure.|التأكد من تغطية الالتزامات والاحتياطيات المحمية قبل التعرض للسوق.|Review income, debt and savings before starting.|راجع الدخل والديون والمدخرات أولاً.|Financial readiness gate based on the original assessment rules.|بوابة الجاهزية حسب قواعد التقييم الأصلية.
حماية رأس المال|Prioritize avoiding loss of principal.|إعطاء الأولوية لتجنب خسارة أصل المال.|Compare low-risk choices and reserve requirements.|قارن البدائل الأقل مخاطرة والاحتياطيات المطلوبة.|Review downside, liquidity and eligible allocation; no universal return formula.|مراجعة الخسارة المحتملة والسيولة والتخصيص المؤهل؛ لا توجد معادلة عائد موحدة.
إدارة السيولة|Keep cash accessible for obligations.|الحفاظ على النقد المتاح للالتزامات.|Match maturities to spending needs.|طابق آجال الاستحقاق مع الاحتياجات.|Cash coverage = available liquid assets / near-term obligations.|تغطية السيولة = الأصول السائلة المتاحة ÷ الالتزامات القريبة.
دخل محافظ|Seek relatively stable income with controlled risk.|السعي لدخل مستقر نسبياً مع ضبط المخاطر.|Compare payout, credit risk and maturity.|قارن التوزيعات ومخاطر الائتمان والاستحقاق.|Income yield = annual cash income / invested capital.|عائد الدخل = الدخل النقدي السنوي ÷ رأس المال المستثمر.
ادخار قصير الأجل|Protect money for a near-term goal.|حماية المال المخصص لهدف قريب.|Match the savings instrument to the goal date.|طابق أداة الادخار مع موعد الهدف.|Future value = principal × (1 + periodic rate)^periods, subject to product terms.|القيمة المستقبلية = الأصل × (1 + معدل الفترة)^عدد الفترات وفق شروط المنتج.
الاستثمار في المؤشرات|Track a broad index through a suitable product.|تتبع مؤشر واسع بأداة مناسبة.|Compare tracking error, fees and diversification.|قارن خطأ التتبع والرسوم والتنويع.|Fund return minus benchmark return; evaluate tracking error.|عائد الصندوق ناقص عائد المؤشر؛ قيّم خطأ التتبع.
الاستثمار في صناديق متنوعة|Spread exposure across holdings via funds.|توزيع التعرض على استثمارات متعددة عبر الصناديق.|Review holdings, fees and concentration.|راجع المكونات والرسوم والتركيز.|Portfolio return = weighted sum of aligned asset returns for a single period.|عائد المحفظة = مجموع عوائد الأصول الموزونة لفترة واحدة.
الاستثمار في صناديق متوازنة|Combine equity and defensive assets.|الجمع بين الأسهم والأصول الدفاعية.|Review allocation and drawdown.|راجع التخصيص والتراجع.|Single-period return = equity weight × equity return + defensive weight × defensive return.|عائد الفترة = وزن الأسهم × عائدها + وزن الأصول الدفاعية × عائدها.
استثمار تخصيص الأصول|Allocate across asset classes according to goals and risk.|توزيع الاستثمار بين فئات الأصول وفق الأهداف والمخاطر.|Set weights and rebalance with cost awareness.|حدد الأوزان وأعد التوازن مع مراعاة التكاليف.|Target units derive from target weight × portfolio value / unit price.|الوحدات المستهدفة من الوزن × قيمة المحفظة ÷ سعر الوحدة.
الشراء والاحتفاظ|Buy and hold over the chosen horizon.|الشراء والاحتفاظ خلال الأفق المحدد.|Compare net performance against a passive benchmark.|قارن الأداء الصافي بمؤشر مرجعي.|Prototype enters at step zero for next-step execution and holds; return = ending / initial equity − 1.|النموذج يدخل عند الخطوة صفر للتنفيذ التالي ويحتفظ؛ العائد = القيمة النهائية ÷ الابتدائية − 1.
استثمار القيمة|Seek a price below an evidence-based estimate of value.|البحث عن سعر أقل من تقدير قيمة مدعوم بالأدلة.|Use compatible multiples and valuation scenarios.|استخدم مضاعفات متوافقة وسيناريوهات تقييم.|Margin of safety = (estimated value − price) / estimated value; estimate uncertain.|هامش الأمان = (القيمة المقدرة − السعر) ÷ القيمة المقدرة؛ التقدير غير مؤكد.
استثمار النمو|Focus on businesses with sustainable expansion.|التركيز على الشركات ذات النمو المستدام.|Compare earnings and revenue growth with valuation.|قارن نمو الأرباح والإيرادات بالتقييم.|Growth = current / prior comparable value − 1.|النمو = القيمة الحالية ÷ السابقة المتوافقة − 1.
استثمار الجودة|Focus on durable financial strength and profitability.|التركيز على القوة المالية والربحية المستدامة.|Review profitability, leverage and cash flow.|راجع الربحية والرافعة والتدفق النقدي.|Use multiple ratios, not one universal quality score.|استخدم عدة نسب؛ لا توجد درجة جودة موحدة.
دخل توزيعات مستقر|Favor sustainable recurring distributions.|تفضيل التوزيعات المتكررة المستدامة.|Check distribution record and cash coverage.|تحقق من تاريخ التوزيعات والتغطية النقدية.|Dividend yield = annual dividend per share / price; payout = dividends / earnings.|عائد التوزيع = التوزيع السنوي للسهم ÷ السعر؛ نسبة التوزيع = التوزيعات ÷ الأرباح.
عائد توزيعات مرتفع|Focus on high dividend yield while checking sustainability.|التركيز على عائد توزيعات مرتفع مع التحقق من الاستدامة.|Avoid treating a falling price as automatic opportunity.|لا تعتبر انخفاض السعر فرصة تلقائياً.|Yield = annual dividend per share / market price.|العائد = التوزيع السنوي للسهم ÷ سعر السوق.
نمو التوزيعات|Focus on businesses growing cash distributions over time.|التركيز على الشركات التي تنمي توزيعاتها عبر الزمن.|Compare adjusted per-share distributions and coverage.|قارن التوزيع المعدل للسهم والتغطية.|Dividend growth = comparable current dividend / prior dividend − 1.|نمو التوزيع = التوزيع الحالي المتوافق ÷ السابق − 1.
النمو بسعر معقول (GARP)|Balance growth potential against valuation.|الموازنة بين فرص النمو والتقييم.|Compare growth, multiples and financial quality.|قارن النمو والمضاعفات والجودة المالية.|PEG = P/E / expected earnings growth in percentage points; assumptions uncertain.|PEG = مضاعف الربحية ÷ نمو الأرباح المتوقع بالنقاط المئوية؛ الافتراضات غير مؤكدة.
الاستثمار الدفاعي|Favor resilience during difficult conditions.|تفضيل القدرة على الصمود في الظروف الصعبة.|Evaluate downside and economic sensitivity.|قيّم الجانب السلبي والحساسية الاقتصادية.|Compare drawdown, volatility and stress tests; no single rule.|قارن التراجع والتذبذب واختبارات الضغط؛ لا توجد قاعدة واحدة.
تداول المراكز|Hold positions based on a sustained trend.|الاحتفاظ بمراكز وفق اتجاه ممتد.|Inspect trend and position risk.|افحص الاتجاه ومخاطر المركز.|Prototype: price above rising SMA5, requiring six prices.|النموذج: السعر أعلى من متوسط SMA5 الصاعد، ويتطلب ستة أسعار.
التداول المتأرجح|Capture short price swings.|استهداف موجات سعرية قصيرة.|Study reversal patterns and costs.|ادرس الانعكاسات والتكاليف.|Prototype enters after positive change following negative change, exits on negative change.|النموذج يدخل بعد تغير موجب يلي تغيراً سالباً ويخرج عند تغير سالب.
اتباع الاتجاه|Trade in the direction of a detected trend.|التداول باتجاه الاتجاه المرصود.|Compare moving averages and test false signals.|قارن المتوسطات واختبر الإشارات الكاذبة.|Prototype: long when SMA3 > SMA5, otherwise cash.|النموذج: شراء عند SMA3 أكبر من SMA5 وإلا نقد.
تداول الزخم|Use recent price strength as an input.|استخدام قوة الحركة السعرية الأخيرة كمدخل.|Compare momentum across a consistent horizon.|قارن الزخم على أفق زمني موحد.|Prototype: long when trailing three-step return > 0.|النموذج: شراء عند عائد آخر ثلاث خطوات أكبر من صفر.
تداول الاختراق|Study movement beyond an earlier price range.|دراسة تجاوز نطاق سعري سابق.|Check the breakout and risk of reversal.|تحقق من الاختراق ومخاطر الانعكاس.|Prototype enters above prior three closes and exits below their minimum.|النموذج يدخل فوق آخر ثلاثة إغلاقات ويخرج تحت أدناها.
تداول التصحيح|Look for a temporary decline within a trend.|البحث عن هبوط مؤقت داخل اتجاه.|Evaluate whether the trend remains intact.|قيّم استمرار الاتجاه.|Prototype enters above SMA5 on a negative one-step return and exits below SMA5.|النموذج يدخل فوق SMA5 عند عائد خطوة سالب ويخرج أسفله.
تداول النطاق|Study oscillation within a price range.|دراسة التذبذب داخل نطاق سعري.|Identify range boundaries and breakout risk.|حدد حدود النطاق ومخاطر الاختراق.|Prototype enters in bottom quarter of prior three-price range and exits in top quarter.|النموذج يدخل في الربع الأدنى لنطاق ثلاثة أسعار سابقة ويخرج في الربع الأعلى.
الارتداد إلى المتوسط|Study deviations from a reference average.|دراسة الانحراف عن متوسط مرجعي.|Measure deviation and test regime dependence.|قس الانحراف واختبر تأثير حالة السوق.|Prototype enters 1% below SMA3 and exits at or above SMA3.|النموذج يدخل تحت SMA3 بنسبة 1% ويخرج عنده أو فوقه.
تداول الانعكاس|Study potential changes in trend direction.|دراسة تغير محتمل في اتجاه السعر.|Use patterns with confirmation and risk controls.|استخدم الأنماط مع التأكيد وضبط المخاطر.|No executable rule in V1.19; patterns are descriptive evidence.|لا توجد قاعدة تنفيذية في V1.19؛ الأنماط أدلة وصفية.
التداول القائم على الأحداث|Study announcements and potential transmission channels.|دراسة الإعلانات وقنوات تأثيرها المحتملة.|Check publication time and uncertainty.|تحقق من توقيت النشر وعدم اليقين.|Event-window return versus aligned benchmark; causal impact is not established.|عائد نافذة الحدث مقابل مؤشر متوافق؛ لا يثبت السببية.
التداول اليومي|Enter and exit during one market session.|الدخول والخروج خلال جلسة واحدة.|Use intraday liquidity and execution training.|استخدم تدريب السيولة والتنفيذ اللحظي.|Net intraday P/L = sale proceeds − purchase cost − fees; actual intraday data pending.|صافي الربح اليومي = حصيلة البيع − تكلفة الشراء − الرسوم؛ البيانات الفعلية غير مكتملة.
المضاربة السريعة|Study very short movements and execution costs.|دراسة الحركات القصيرة جداً وتكاليف التنفيذ.|Inspect spread and slippage before testing.|افحص الفارق السعري والانزلاق قبل الاختبار.|Net gain = price movement × quantity − transaction costs; no executable rule yet.|صافي الربح = حركة السعر × الكمية − تكاليف المعاملة؛ لا توجد قاعدة تنفيذية بعد.
القوة النسبية|Compare an investment's movement with a benchmark.|مقارنة حركة الاستثمار بمؤشر مرجعي.|Use matched observation dates.|استخدم تواريخ رصد متطابقة.|Prototype long when own three-step return exceeds EGX30 and is positive.|النموذج يدخل إذا تجاوز عائد ثلاث خطوات عائد EGX30 وكان موجباً.
الدخل المختلط|Combine income sources with different characteristics.|الجمع بين مصادر دخل مختلفة الخصائص.|Review cash flows and concentration.|راجع التدفقات النقدية والتركيز.|Total cash income = sum of eligible distributions; total return includes price change.|إجمالي الدخل = مجموع التوزيعات المؤهلة؛ العائد الكلي يشمل تغير السعر.
المحفظة الأساسية والفرعية|Combine a diversified core with smaller active positions.|الجمع بين محفظة أساسية متنوعة ومراكز نشطة أصغر.|Set separate core and satellite limits.|حدد حدوداً منفصلة للأساسي والفرعي.|Target allocation = core weight + satellite weights + cash weight = 100%.|التخصيص المستهدف = وزن الأساسي + الأوزان الفرعية + النقد = 100%.
الاستثمار والتداول|Separate long-term investing from active trading.|فصل الاستثمار طويل الأجل عن التداول النشط.|Track each sleeve separately with risk limits.|تابع كل جزء منفصلاً مع حدود المخاطر.|Combined value = investment sleeve + trading sleeve + cash; track costs separately.|القيمة المجمعة = الجزء الاستثماري + جزء التداول + النقد؛ تابع التكاليف منفصلة.
التكيف مع السوق|Adapt analytical conditions to market behavior.|تكييف الشروط التحليلية مع سلوك السوق.|Compare evidence across market regimes.|قارن الأدلة عبر حالات السوق.|Prototype: long when own and EGX30 three-step returns are positive.|النموذج يدخل عند عائد موجب لآخر ثلاث خطوات للأصل وEGX30.'''
reg=list(csv.DictReader((BASE/'backtest_registry.csv').open()));assert len(reg)==35
for row,line in zip(reg,strategies.splitlines()):
    ar,m,ma,u,ua,c,ca=line.split('|');add(row['id'],'strategy',row['name'],ar,m,ma,u,ua,c,ca,[row['id']+' '+row['name']],row['status'])
# Each row: ID | English label | Arabic label | meaning EN | meaning AR | use EN | use AR | formula EN | formula AR
metrics='''return_pct|Return|العائد|Change in investment value.|التغير في قيمة الاستثمار.|Compare aligned periods and costs.|قارن فترات وتكاليف متوافقة.|100 × (ending / starting equity − 1)|100 × (القيمة النهائية ÷ الابتدائية − 1)
interval_return|Interval return|عائد الفترة|Price change between observations.|تغير السعر بين رصدين.|Check data interval first.|تحقق من مدة الفترة أولاً.|P(t) / P(t−1) − 1|سعر الفترة ÷ السعر السابق − 1
max_drawdown_pct|Maximum drawdown|أقصى تراجع|Largest peak-to-trough decline.|أكبر انخفاض من قمة إلى قاع.|Compare downside of strategies.|قارن الجانب السلبي للاستراتيجيات.|100 × max(1 − value / prior running peak)|100 × أكبر (1 − القيمة ÷ أعلى قيمة سابقة)
drawdown|Drawdown|التراجع|Decline from the running peak.|الانخفاض من أعلى قيمة سابقة.|Monitor risk through time.|راقب المخاطر عبر الزمن.|1 − value / running peak|1 − القيمة ÷ أعلى قيمة حتى الآن
volatility|Volatility|التذبذب|Dispersion of periodic returns.|تشتت عوائد الفترات.|Compare using same frequency.|قارن بنفس التواتر.|Sample standard deviation of returns.|الانحراف المعياري للعوائد.
sharpe|Sharpe ratio|نسبة شارب|Excess return per unit of total volatility.|العائد الزائد لكل وحدة تذبذب.|Require compatible risk-free rate and interval.|يتطلب معدل خالٍ من المخاطر وفترة متوافقة.|mean(R − Rf) / sd(R)|متوسط (العائد − الخالي من المخاطر) ÷ انحراف العائد
sortino|Sortino ratio|نسبة سورتينو|Excess return relative to downside deviation.|العائد الزائد بالنسبة للانحراف السلبي.|Use an explicit target return.|حدد العائد المستهدف.|mean(R − target) / downside deviation|متوسط (العائد − المستهدف) ÷ الانحراف السلبي
calmar|Calmar ratio|نسبة كالمار|Annualized return relative to maximum drawdown.|العائد السنوي نسبة إلى أقصى تراجع.|Requires sufficient annualization evidence.|يتطلب أدلة كافية للتحويل السنوي.|Annualized return / maximum drawdown|العائد السنوي ÷ أقصى تراجع
alpha|Alpha|ألفا|Intercept of excess-return benchmark regression.|ثابت انحدار العائد الزائد مقابل المؤشر.|Use aligned returns and risk-free rate.|استخدم عوائد متزامنة ومعدل خالٍ من المخاطر.|mean(Rp−Rf) − beta × mean(Rb−Rf)|متوسط عائد المحفظة الزائد − بيتا × متوسط عائد المؤشر الزائد
beta|Beta|بيتا|Sensitivity to benchmark returns.|الحساسية لعائد المؤشر المرجعي.|Check benchmark relevance.|تحقق من ملاءمة المؤشر.|cov(Rp,Rb) / var(Rb)|التغاير ÷ تباين عائد المؤشر
correlation|Correlation|الارتباط|Linear co-movement of two return series.|الحركة الخطية المشتركة لسلسلتين.|Use matched periods; not causation.|استخدم فترات متوافقة؛ ليس سببية.|cov(X,Y)/(sd(X)×sd(Y))|التغاير ÷ حاصل ضرب الانحرافين
tracking_error|Tracking error|خطأ التتبع|Variability of active returns.|تذبذب العائد النشط.|Compare a fund with its benchmark.|قارن الصندوق بمؤشره.|sd(Rp − Rb)|الانحراف المعياري لفارق العائد
information_ratio|Information ratio|نسبة المعلومات|Active return per unit of tracking error.|العائد النشط لكل وحدة خطأ تتبع.|Compare active strategy consistency.|قارن اتساق الاستراتيجيات النشطة.|mean(Rp − Rb) / sd(Rp − Rb)|متوسط فارق العائد ÷ انحرافه
cvar|CVaR loss|الخسارة المتوقعة في الذيل|Expected loss in the worst tail of modeled outcomes.|متوسط الخسارة في أسوأ ذيل من النتائج النموذجية.|Change confidence and penalty; results depend on scenarios.|غيّر مستوى الثقة والعقوبة؛ تعتمد النتيجة على السيناريوهات.|min over t≥0 of t + mean(max(L−t,0))/(1−α).|أقل قيمة لـ t + متوسط max(L−t,0) ÷ (1−α) حيث t غير سالب.
var|Value at risk|القيمة المعرضة للمخاطر|Loss quantile under a chosen model.|كمية الخسارة عند مستوى احتمال محدد.|Use alongside tail risk.|استخدمها مع مخاطر الذيل.|Loss quantile at confidence α.|كمية الخسارة عند مستوى الثقة α.
expected_return_pct|Expected return|العائد المتوقع|Mean modeled future portfolio return.|متوسط العائد المستقبلي النموذجي.|Review forecasts; not a promise.|راجع التوقعات؛ ليست ضماناً.|100 × average terminal return across scenarios.|100 × متوسط العائد النهائي عبر السيناريوهات.
equity|Equity|قيمة المحفظة|Marked value of cash and holdings.|قيمة النقد والحيازات بسعر التقييم.|Track changes after orders.|تابع التغير بعد الأوامر.|Cash + Σ(units × mark).|النقد + مجموع (الوحدات × سعر التقييم).
cash|Cash|النقد|Available uninvested cash.|النقد غير المستثمر المتاح.|Check affordability and reserves.|تحقق من القدرة الشرائية والاحتياطيات.|Prior cash − buy cost + sell proceeds − fees.|النقد السابق − تكلفة الشراء + حصيلة البيع − الرسوم.
exposure|Exposure|التعرض|Value subject to asset price risk.|القيمة المعرضة لمخاطر السعر.|Check concentration and caps.|تحقق من التركيز والحدود.|Σ holdings × marks / portfolio equity.|مجموع الحيازات × أسعار التقييم ÷ قيمة المحفظة.
turnover|Turnover|دوران التداول|Traded notional relative to starting equity.|قيمة التداول نسبة إلى القيمة الابتدائية.|Limit transaction frequency and cost.|حد من تكرار التداول وتكلفته.|Σ(abs(traded units) × mark) / pretrade equity.|مجموع (القيمة المطلقة للوحدات المتداولة × السعر) ÷ القيمة قبل التداول.
fee|Fee|الرسوم|Charge for simulated execution.|تكلفة التنفيذ المحاكى.|Inspect assumed basis points.|افحص نقاط الأساس المفترضة.|Notional × bps / 10,000 (engine rounds in cents).|القيمة × نقاط الأساس ÷ 10000 (التقريب بالقروش).
spread|Bid–ask spread|الفارق بين العرض والطلب|Difference between ask and bid.|الفرق بين سعر الطلب والعرض.|Evaluate execution costs.|قيّم تكاليف التنفيذ.|Ask − bid; relative spread = difference / mid.|الطلب − العرض؛ الفارق النسبي = الفرق ÷ الوسط.
slippage|Slippage|الانزلاق السعري|Difference between expected and simulated execution price.|الفرق بين السعر المتوقع وسعر التنفيذ المحاكى.|Stress-test assumptions.|اختبر الافتراضات تحت الضغط.|Execution price − reference price, with side-aware sign.|سعر التنفيذ − المرجع مع مراعاة اتجاه الصفقة.
nav|NAV|صافي قيمة الأصول|Per-unit value of a fund.|قيمة الوحدة بالصندوق.|Compare same fund and denomination.|قارن الصندوق نفسه وفئة الوحدة.|(Assets − liabilities) / outstanding units.|(الأصول − الالتزامات) ÷ الوحدات القائمة.
pe|P/E|مضاعف الربحية|Price per unit of earnings per share.|السعر مقابل ربح السهم.|Compare compatible positive earnings.|قارن أرباحاً موجبة ومتوافقة.|Price / EPS.|السعر ÷ ربح السهم.
pb|P/B|مضاعف القيمة الدفترية|Price per unit of book value.|السعر مقابل القيمة الدفترية.|Review accounting basis and sector.|راجع الأساس المحاسبي والقطاع.|Price / book value per share.|السعر ÷ القيمة الدفترية للسهم.
dcf|Discounted cash flow|التدفقات النقدية المخصومة|Present value of hypothetical future cash flows.|القيمة الحالية للتدفقات المستقبلية المفترضة.|Use non-bank compatible cash flows; vary WACC and growth.|استخدم تدفقات متوافقة للشركات غير المصرفية وغيّر الخصم والنمو.|EV = Σ FCFFt/(1+WACC)^t + discounted terminal value; equity = EV−net debt.|قيمة المنشأة = مجموع التدفقات المخصومة + القيمة النهائية المخصومة؛ حقوق الملكية = قيمة المنشأة − صافي الدين.
wacc|WACC|المتوسط المرجح لتكلفة رأس المال|Blended financing discount rate.|معدل خصم تمويلي مرجح.|Must exceed terminal growth in perpetuity model.|يجب أن يتجاوز النمو النهائي في النموذج الدائم.|E/(D+E)×Re + D/(D+E)×Rd×(1−tax).|وزن حقوق الملكية × تكلفتها + وزن الدين × تكلفته بعد الضريبة.
leverage|Leverage|الرافعة المالية|Exposure relative to own equity.|التعرض نسبة إلى حقوق المستثمر.|Use static stress lab only; margin trading disabled.|استخدم مختبر الضغط الثابت فقط؛ التداول بالهامش معطل.|Exposure / equity; static equity change = exposure × asset return.|التعرض ÷ حقوق المستثمر؛ تغير الحقوق = التعرض × عائد الأصل.
market_breadth|Market breadth|اتساع السوق|Number of advancing versus declining proxies.|عدد الأصول الصاعدة مقابل الهابطة.|Inspect participation, not just index direction.|افحص المشاركة لا اتجاه المؤشر فقط.|Count up, down and flat; advancing share = up / total.|عد الصاعد والهابط والثابت؛ حصة الصعود = الصاعد ÷ الإجمالي.
real_return|Real return|العائد الحقيقي|Purchasing-power change after inflation.|تغير القوة الشرائية بعد التضخم.|Use same-period inflation.|استخدم التضخم للفترة ذاتها.|(1+nominal return)/(1+inflation)−1.|(1 + العائد الاسمي) ÷ (1 + التضخم) − 1.
fx_return|Currency-adjusted return|العائد المعدل بالعملة|Investment return expressed in another currency.|العائد بعملة أخرى.|Align currencies and FX direction.|طابق العملات واتجاه الصرف.|For USD asset in EGP: (1+USD return)×(1+USD/EGP change)−1.|لأصل بالدولار بالجنيه: (1 + عائد الدولار) × (1 + تغير الدولار/الجنيه) − 1.
benchmark|Benchmark|المؤشر المرجعي|Reference used to compare performance.|مرجع لمقارنة الأداء.|Match time period, basis and costs.|طابق الفترة والأساس والتكاليف.|Relative return = portfolio return − reference return.|العائد النسبي = عائد المحفظة − عائد المرجع.
position_stop|Position stop|وقف خسارة المركز|Conditional exit when modeled position loss crosses a limit.|خروج مشروط عند تجاوز خسارة المركز حداً.|Set threshold; zero disables in backtest.|حدد الحد؛ الصفر يعطله في الاختبار.|Compare loss against threshold; next-step fill is not guaranteed at stop.|قارن الخسارة بالحد؛ التنفيذ التالي ليس مضموناً عند سعر الوقف.'''
for line in metrics.splitlines():
    a=line.split('|'); add(a[0],'metric',*a[1:],aliases=[a[0].replace('_',' ')])
# Fundamental metrics derived from exact existing engine output, with specific labels and formula.
fm={
'equity_assets':('Equity / assets','حقوق الملكية / الأصول','total equity / total assets','حقوق الملكية ÷ إجمالي الأصول'), 'liabilities_assets':('Liabilities / assets','الالتزامات / الأصول','total liabilities / total assets','الالتزامات ÷ إجمالي الأصول'), 'profit_ending_assets':('Profit / ending assets','الربح / أصول نهاية الفترة','net profit / ending assets (not ROA using average assets)','صافي الربح ÷ أصول نهاية الفترة (ليس ROA بمتوسط الأصول)'), 'profit_ending_equity':('Profit / ending equity','الربح / حقوق نهاية الفترة','net profit / ending equity (not ROE using average equity)','صافي الربح ÷ حقوق نهاية الفترة (ليس ROE بمتوسط الحقوق)'), 'balance_sheet_residual':('Balance sheet residual','فرق الميزانية','assets − liabilities − equity','الأصول − الالتزامات − حقوق الملكية'), 'cash_capex_revenue':('Cash CAPEX / revenue','الإنفاق الرأسمالي النقدي / الإيراد','cash CAPEX / revenue','الإنفاق الرأسمالي النقدي ÷ الإيراد'), 'ebitda_margin':('EBITDA margin','هامش EBITDA','EBITDA / revenue','الأرباح قبل الفوائد والضرائب والإهلاك والاستهلاك ÷ الإيراد'), 'fcff_margin':('Reported FCFF margin','هامش التدفق الحر المعلن','reported FCFF / revenue','التدفق النقدي الحر المعلن للمنشأة ÷ الإيراد'), 'net_profit_margin':('Net profit margin','هامش صافي الربح','net profit / revenue','صافي الربح ÷ الإيراد'), 'effective_tax_rate':('Effective tax rate','معدل الضريبة الفعلي','absolute tax expense / profit before tax','القيمة المطلقة لمصروف الضريبة ÷ الربح قبل الضريبة'), 'loans_deposits':('Loans / deposits','القروض / الودائع','net customer loans / customer deposits','صافي قروض العملاء ÷ ودائع العملاء')}
yoy={'assets_highlights':'Assets (highlights)|الأصول (الملخص)','customer_deposits':'Customer deposits|ودائع العملاء','deposits_highlights':'Deposits (highlights)|الودائع (الملخص)','net_operating_income':'Net operating income|صافي الدخل التشغيلي','net_profit_as_disclosed':'Disclosed net profit|صافي الربح المعلن','net_profit_highlights':'Net profit (highlights)|صافي الربح (الملخص)','net_profit':'Net profit|صافي الربح','total_assets':'Total assets|إجمالي الأصول','total_equity':'Total equity|إجمالي حقوق الملكية','revenue':'Revenue|الإيراد','fcff_reported':'Reported FCFF|التدفق النقدي الحر المعلن'}
for k,v in yoy.items():
    en,ar=v.split('|');fm[k+'_yoy']=(en+' YoY growth','نمو '+ar+' السنوي','(current comparable value / positive prior value − 1) × 100','(القيمة الحالية المتوافقة ÷ القيمة السابقة الموجبة − 1) × 100')
for k,(en,ar,c,ca) in fm.items():add(k,'metric',en,ar,'Financial statement indicator on the reported basis.','مؤشر للقوائم المالية وفق الأساس المعلن.','Compare compatible periods and accounting scopes; inspect source inputs.','قارن الفترات والنطاقات المحاسبية المتوافقة وافحص المصدر.',c+(' × 100' if k not in ('balance_sheet_residual',) and not k.endswith('_yoy') else ''),ca+(' × 100' if k not in ('balance_sheet_residual',) and not k.endswith('_yoy') else ''),[k.replace('_',' ')])
# Technical calculations and exact keys.
for n in (3,5,20,50,200):add('sma'+str(n),'metric',f'SMA {n}',f'المتوسط المتحرك البسيط {n}','Average of recent closing observations.','متوسط الإغلاقات الأخيرة.','Compare price and average; requires complete window.','قارن السعر والمتوسط؛ يتطلب اكتمال النافذة.',f'Sum of last {n} closes / {n}.',f'مجموع آخر {n} إغلاقات ÷ {n}.',[f'SMA{n}'])
for n in (5,12,26):add('ema'+str(n),'metric',f'EMA {n}',f'المتوسط المتحرك الأسي {n}','Weighted average emphasizing recent prices.','متوسط مرجح يعطي وزناً للأسعار الحديثة.','Inspect trend; requires warm-up.','افحص الاتجاه؛ يتطلب فترة تهيئة.',f'Initial SMA; EMA = P×2/({n}+1) + prior EMA×(1−2/({n}+1)).',f'بداية بمتوسط بسيط؛ السعر × 2/({n}+1) + المتوسط السابق × (1−2/({n}+1)).',[f'EMA{n}'])
for n in (3,14):add('rsi'+str(n),'metric',f'RSI {n}',f'مؤشر القوة النسبية {n}','Momentum oscillator between 0 and 100.','مؤشر زخم بين صفر و100.','Study momentum, not an automatic order.','ادرس الزخم وليس أمراً تلقائياً.','100 − 100/(1+Wilder average gain / average loss).','100 − 100 ÷ (1 + متوسط المكاسب بطريقة وايلدر ÷ متوسط الخسائر).',[f'RSI{n}'])
for line in '''macd|MACD|ماكد|Difference of short and long exponential averages.|فرق المتوسطين الأسيين القصير والطويل.|Inspect momentum and crossovers.|افحص الزخم والتقاطعات.|EMA12 − EMA26.|المتوسط الأسي 12 − المتوسط الأسي 26.
macd_signal|MACD signal|خط إشارة ماكد|Smoothed MACD.|ماكد بعد التنعيم.|Compare with MACD.|قارنه بماكد.|EMA9 of MACD.|المتوسط الأسي 9 لماكد.
macd_hist|MACD histogram|مدرج ماكد|Difference from signal line.|الفرق عن خط الإشارة.|Monitor momentum changes.|راقب تغير الزخم.|MACD − signal.|ماكد − الإشارة.
bb_upper|Bollinger upper|حد بولينجر الأعلى|Upper volatility band.|الحد العلوي للتذبذب.|Inspect deviations; requires 20 closes.|افحص الانحراف؛ يتطلب 20 إغلاقاً.|SMA20 + 2 × population SD20.|متوسط 20 + ضعفي الانحراف المعياري السكاني.
bb_lower|Bollinger lower|حد بولينجر الأدنى|Lower volatility band.|الحد الأدنى للتذبذب.|Inspect deviations.|افحص الانحراف.|SMA20 − 2 × population SD20.|متوسط 20 − ضعفي الانحراف المعياري السكاني.
atr14|ATR 14|متوسط المدى الحقيقي 14|Smoothed true price range.|متوسط المدى الحقيقي المنعم.|Compare volatility in price units.|قارن التذبذب بوحدات السعر.|Wilder average of max(H−L, abs(H−prior C), abs(L−prior C)).|متوسط وايلدر لأكبر (الأعلى−الأدنى، الفرق المطلق للأعلى أو الأدنى مع الإغلاق السابق).
stoch14|Stochastic %K|مؤشر ستوكاستيك %K|Close relative to recent high-low range.|الإغلاق نسبة لنطاق أعلى وأدنى سعر.|Use compatible OHLC history.|استخدم تاريخ OHLC متوافقاً.|100 × (C−lowest L14)/(highest H14−lowest L14).|100 × (الإغلاق−أدنى قاع14) ÷ (أعلى قمة14−أدنى قاع14).
obv|OBV|حجم التداول التراكمي الاتجاهي|Cumulative signed volume.|حجم تداول تراكمي باتجاه السعر.|Use meaningful vendor volume only.|استخدم حجم تداول موثوق المعنى.|Previous OBV + sign(close change)×volume.|OBV السابق + إشارة تغير الإغلاق × الحجم.
vwap|VWAP|متوسط السعر المرجح بالحجم|Volume-weighted average of revealed synthetic trades.|متوسط سعر الصفقات الاصطناعية المكشوفة مرجحاً بالحجم.|Intraday exercise only.|تمرين لحظي فقط.|Σ(price×allocated volume) / Σ(volume).|مجموع (السعر × الحجم المخصص) ÷ مجموع الحجم.
volume_ratio5|Relative volume|الحجم النسبي|Current volume versus prior five observations.|الحجم الحالي مقابل آخر خمس رصدات.|Look for anomalies; not causation.|ابحث عن الشذوذ؛ لا يثبت السببية.|Current volume / mean(previous five volumes).|الحجم الحالي ÷ متوسط الأحجام الخمسة السابقة.
support5|Support|الدعم|Lowest previous five closes.|أدنى خمسة إغلاقات سابقة.|Inspect a simple prior level.|افحص مستوى سابقاً بسيطاً.|min(previous 5 closes).|أدنى آخر خمسة إغلاقات قبل الحالي.
resistance5|Resistance|المقاومة|Highest previous five closes.|أعلى خمسة إغلاقات سابقة.|Inspect breakout reference.|افحص مرجع الاختراق.|max(previous 5 closes).|أعلى آخر خمسة إغلاقات قبل الحالي.
engulfing|Engulfing pattern|نمط الابتلاع|Two-candle body engulfing with opposite colors.|ابتلاع جسم شمعة لأخرى باتجاه معاكس.|Inspect pattern with context.|افحص النمط مع السياق.|Compare current and preceding open/close body endpoints.|قارن طرفي جسم الشمعة الحالية والسابقة.
doji|Doji|دوجي|Small candle body relative to range.|جسم شمعة صغير نسبة إلى مداها.|Inspect potential indecision.|افحص احتمال التردد.|abs(close−open) ≤ threshold×(high−low).|القيمة المطلقة (الإغلاق−الافتتاح) ≤ الحد × (الأعلى−الأدنى).'''.splitlines():a=line.split('|');add(a[0],'metric',*a[1:],aliases=[a[0].replace('_',' ')])
# Workspace/tool and algorithm reference entries.
tools='''assessment|Investor assessment|تقييم المستثمر|Adaptive financial and personality assessment.|تقييم تكيفي للظروف المالية والشخصية.|Enter fictional inputs, answer questions and review conflicts.|أدخل بيانات افتراضية وأجب عن الأسئلة وراجع التعارضات.|Frozen V4.1 rules, evidence gates and financial solvers; no live authorization.|قواعد V4.1 وبوابات الأدلة والحلول المالية؛ لا تصريح تداول فعلي.
plan|Conditional plan|الخطة المشروطة|Modeled allocation and goals subject to eligibility.|تخصيص وأهداف نموذجية مشروطة بالأهلية.|Review restrictions and verify assumptions.|راجع القيود وتحقق من الافتراضات.|Existing financial readiness and allocation engine; approved live allocation = 0.|محرك الجاهزية والتخصيص القائم؛ التخصيص الفعلي المصرح = صفر.
academy|Trading Academy|أكاديمية التداول|Lessons, curricula and recorded knowledge checks.|دروس ومناهج واختبارات معرفة مسجلة.|Complete prerequisites, study and submit quizzes.|أكمل المتطلبات وادرس وأرسل الاختبار.|Score = correct answers; completion requires full marks.|الدرجة = الإجابات الصحيحة؛ الإكمال يتطلب الدرجة الكاملة.
progress|Investor evidence journal|سجل أدلة المستثمر|Recorded assessment, learning and simulated actions.|سجل التقييم والتعلم والإجراءات المحاكاة.|Review history; do not infer risk tolerance automatically.|راجع التاريخ؛ لا تستنتج تحمل المخاطر تلقائياً.|Counts persisted events, fills, rejections and computed returns.|عد الأحداث والتنفيذ والرفض والعوائد المحسوبة.
market|Augmented Market World|عالم السوق المعزز|Synthetic market replay with global factors and virtual orders.|إعادة تشغيل سوق اصطناعي بعوامل عالمية وأوامر افتراضية.|Choose scenario, instrument and advance steps.|اختر السيناريو والأصل وتقدم خطوة بخطوة.|Reveal chronological price prefix; fill at next step with modeled fees.|عرض الأسعار حتى الخطوة الحالية؛ التنفيذ في الخطوة التالية برسوم نموذجية.
fundamental|Fundamental analysis|التحليل الأساسي|Financial statement, fund and valuation evidence.|أدلة القوائم المالية والصناديق والتقييم.|Choose an instrument and optional cutoff; inspect source and basis.|اختر الأصل وتاريخ القطع الاختياري وافحص المصدر والأساس.|Ratios from compatible observations; scenario models use explicit assumptions.|نسب من مشاهدات متوافقة؛ النماذج تستخدم افتراضات صريحة.
technical|Technical analysis|التحليل الفني|Price, momentum, trend and volume indicators.|مؤشرات السعر والزخم والاتجاه والحجم.|Select observed sample or revealed simulation prefix.|اختر عينة مرصودة أو الجزء المكشوف من المحاكاة.|Calculate trailing indicators only when history is sufficient.|حساب المؤشرات المتأخرة فقط عند كفاية التاريخ.
intelligence|Market Intelligence Lab|مختبر ذكاء السوق|Integrates dated news, macro reports and market conditions.|دمج الأخبار المؤرخة والتقارير الاقتصادية وظروف السوق.|Select cutoff or saved replay; inspect disagreement and uncertainty.|اختر تاريخ القطع أو محاكاة محفوظة وافحص التعارض وعدم اليقين.|Rule-based classification, latest eligible vintage and directional comparison.|تصنيف بالقواعد وأحدث إصدار متاح ومقارنة اتجاهية.
backtest|Strategy Backtesting Lab|مختبر اختبار الاستراتيجيات|Chronological simulated strategy evaluation.|تقييم استراتيجية بمحاكاة زمنية.|Select a supported rule and scenario; compare benchmark and costs.|اختر قاعدة وسيناريو مدعومين وقارن المرجع والتكاليف.|Rule at t, hypothetical fill at t+1; reconcile cash, shares and fees.|القاعدة عند t والتنفيذ الافتراضي عند t+1؛ تسوية النقد والوحدات والرسوم.
optimizer|Operations Research Lab|مختبر بحوث العمليات|Constrained integer buy/sell and allocation optimization.|تحسين كميات الشراء والبيع والتخصيص بأعداد صحيحة وقيود.|Set horizon, capital and risk controls; run synthetic experiment.|حدد الأفق ورأس المال وضوابط المخاطر وشغّل تجربة اصطناعية.|Maximize expected terminal return − λ×CVaR, subject to cash, holdings, turnover and caps.|تعظيم العائد النهائي المتوقع − λ×CVaR تحت قيود النقد والحيازات والدوران والحدود.
historical|Historical Market Replay|إعادة تشغيل السوق التاريخي|Chronological observed ADIB/EGX30 candidate and extended synthetic paths.|عينة مرصودة مرشحة لـ ADIB وEGX30 ومسارات اصطناعية ممتدة.|Choose date and inspect only available information; acknowledge candidate experiment.|اختر التاريخ وافحص المعلومات المتاحة فقط وأقر بطبيعة التجربة المرشحة.|Matched dates, prior-only bootstrap and next observed open; verification gate closed.|تواريخ متطابقة ومعاينة من الماضي فقط والافتتاح التالي المرصود؛ بوابة التحقق مغلقة.
integration|Integration audit|تدقيق التكامل|Implementation inventory and evidence status.|قائمة التنفيذ وحالة الأدلة.|Review remaining gaps before acceptance.|راجع الفجوات قبل القبول.|Counts by status; not formal acceptance of locked capability definitions.|عد العناصر حسب الحالة؛ ليس قبولاً رسمياً للتعريفات المقفلة.
milp|MILP|البرمجة الخطية المختلطة الصحيحة|Optimization with integer quantities and continuous risk variables.|تحسين بكميات صحيحة ومتغيرات مخاطر مستمرة.|Use constrained OR experiments; no trade on solver failure.|استخدم تجارب بحوث العمليات المقيدة؛ لا صفقة عند فشل الحل.|Minimize linear loss and CVaR with binary direction and integer buys/sells. Android fallback solves LP relaxations and branches on fractional variables.|تقليل الخسارة الخطية وCVaR مع اتجاه ثنائي وكميات صحيحة؛ بديل أندرويد يحل الاسترخاء الخطي ويتفرع عند القيم الكسرية.
bootstrap|Block bootstrap|إعادة المعاينة بالكتل|Samples contiguous past returns to create modeled paths.|معاينة عوائد سابقة متجاورة لتوليد مسارات نموذجية.|Use only revealed history or independent development scenarios.|استخدم التاريخ المكشوف فقط أو سيناريوهات تطوير مستقلة.|Sample synchronized blocks with replacement and compound returns.|معاينة كتل متزامنة مع الإرجاع وتركيب العوائد.
market_regime|Market regime|حالة السوق|Descriptive classification of price behavior.|تصنيف وصفي لسلوك السعر.|Inspect trend or stress; thresholds provisional.|افحص الاتجاه أو الضغط؛ الحدود مؤقتة.|Phase 10.9 trailing 3 intervals: stress if drawdown ≥10%; up/down if cumulative return ≥5% / ≤−5%, otherwise range.|آخر 3 فترات: ضغط عند تراجع 10% فأكثر؛ صعود/هبوط عند عائد 5% فأكثر أو −5% فأقل وإلا نطاق.
source_gate|Historical verification gate|بوابة التحقق التاريخي|Separates candidate observations from verified history.|تفصل المشاهدات المرشحة عن التاريخ المتحقق.|Inspect rights, availability, adjustments and source discrepancies.|افحص الحقوق والإتاحة والتعديلات وفروق المصادر.|Strict eligibility requires independently verified provenance and completeness; currently blocked.|الأهلية الصارمة تتطلب تحقق المصدر والاكتمال؛ مغلقة حالياً.
fund_fee|Fund fee model|نموذج رسوم الصندوق|Estimates net hypothetical fund redemption value.|يقدر قيمة الاسترداد الصافية الافتراضية.|Set entry fee, gross return and exit fee.|حدد رسوم الدخول والعائد الإجمالي والخروج.|Capital × (1−entry fee) × (1+gross return) × (1−exit fee).|رأس المال × (1−رسوم الدخول) × (1+العائد الإجمالي) × (1−رسوم الخروج).
fx_sensitivity|Economic sensitivity|الحساسية الاقتصادية|Static cost and interest-rate stress model.|نموذج ضغط ثابت للتكاليف والفائدة.|Vary imported-cost share, FX and debt rates.|غيّر حصة التكلفة المستوردة والصرف وفائدة الدين.|Incremental cost = operating costs×import share×FX shock + variable debt×rate shock.|التكلفة الإضافية = التشغيل × حصة الاستيراد × صدمة الصرف + الدين المتغير × صدمة الفائدة.
multiple|Valuation multiples|مضاعفات التقييم|Hypothetical per-share valuation using earnings or book value.|تقييم افتراضي للسهم باستخدام الربح أو القيمة الدفترية.|Enter explicit multiple and per-share metric.|أدخل المضاعف ومؤشر السهم صراحة.|Implied price = per-share input × assumed multiple.|السعر الضمني = مدخل السهم × المضاعف المفترض.
liquidity_cap|Liquidity cap|حد السيولة|Limits virtual order size using prior volume proxy.|يحد حجم الأمر الافتراضي باستخدام حجم سابق كبديل.|Review prior daily volume and assumption.|راجع حجم التداول السابق والافتراض.|Candidate historical experiment uses 1% of preceding reported volume, not executable capacity.|التجربة التاريخية المرشحة تستخدم 1% من الحجم السابق المعلن؛ ليست سعة تنفيذية فعلية.'''
for line in tools.splitlines():a=line.split('|');add(a[0],'tool',*a[1:])
# extra alias matching UI strings
extra={'assessment':['Live-input assessment','Initial financial intake','Start adaptive assessment','Start assessment'], 'plan':['Calculated conditional plan','Calculate conditional plan','Financial goals'], 'market':['Start replay','Advance one step','Virtual portfolio','Queue buy','Queue sell'], 'technical':['Technical Lab','Open Technical Lab'], 'fundamental':['Fundamental Lab','Open Fundamental Lab','Understand the investment behind the price','Calculated indicators'], 'intelligence':['Market context & evidence','Open Intelligence Lab'], 'backtest':['Strategy Backtesting','Run experiment','Performance comparison','Open Backtesting Lab'], 'optimizer':['Integer Portfolio Optimization','Optimize and replay','Open Optimization Lab','Decision model','Solver decisions'], 'historical':['Historical Replay Lab','Run candidate experiment','Open Historical Replay Lab'], 'progress':['Investor evidence','Review evidence'], 'integration':['Integration status','View audit','Phase 19 · Implementation audit'], 'academy':['Open Academy','Learning progress','Curriculum by strategy'], 'cvar':['CVaR loss %','CVaR confidence (0.50–0.99)','Downside penalty λ','CVaR'], 'expected_return_pct':['Expected return %'], 'return_pct':['Return %','Total return','Return pct'], 'max_drawdown_pct':['Max drawdown','Maximum drawdown %','Portfolio drawdown lock (%) · 0 disables'], 'position_stop':['Position stop (%) · 0 disables'], 'exposure':['Single asset cap %','Total exposure cap %','Entry allocation (%)'], 'fee':['Transaction fee (bps)','Commission (bps)'], 'turnover':['Per-step turnover cap %'], 'spread':['Normal half-spread (bps)','Stress half-spread (bps)'], 'slippage':['Extra slippage (bps)','Half spread + slippage (bps)'], 'equity':['Equity EGP','Virtual equity'], 'cash':['Initial available cash (virtual EGP)','Cash reserve %'], 'leverage':['Leverage stress lab','Exposure multiple'], 'source_gate':['Verification gate','Check actual historical eligibility'], 'dcf':['Corporate discounted cash flow','DCF'], 'fund_fee':['Fund fees and net return'], 'fx_sensitivity':['FX and interest-rate sensitivity'], 'multiple':['Per-share multiple (P/E or P/B assumption)'],'vwap':['synthetic_vwap','synthetic vwap'],'doji':['doji_10pct_range'],'engulfing':['bullish_body_engulfing','bearish_body_engulfing'],'return_pct':['Return %','Total return','Return pct','Strategy return','Optimizer return','Passive return','Buy & hold return'],'equity':['Equity EGP','Virtual equity','Ending equity'],'fee':['Transaction fee (bps)','Commission (bps)','Costs'],'benchmark':['EGX30 gross factor']}
for e in entries:e['aliases']+=extra.get(e['id'],[])
# UI translations: only visible exact labels, never mutate machine values.
labels='''Sign out|تسجيل الخروج
Local investor account|حساب المستثمر المحلي
Account alias|اسم الحساب
Password (12+ characters)|كلمة المرور (12 حرفاً فأكثر)
Sign in|تسجيل الدخول
Create account|إنشاء حساب
Assessment, practice and progress|التقييم والتدريب والتقدم
Start assessment|ابدأ التقييم
New replay|محاكاة جديدة
Fundamental analysis|التحليل الأساسي
Open Fundamental Lab|فتح مختبر التحليل الأساسي
Technical analysis|التحليل الفني
Open Technical Lab|فتح مختبر التحليل الفني
Market Intelligence Lab|مختبر ذكاء السوق
Open Intelligence Lab|فتح مختبر ذكاء السوق
Strategy Backtesting Lab|مختبر اختبار الاستراتيجيات
Open Backtesting Lab|فتح مختبر الاختبار
Operations Research Lab|مختبر بحوث العمليات
Open Optimization Lab|فتح مختبر التحسين
Historical Market Replay|إعادة تشغيل السوق التاريخي
Open Historical Replay Lab|فتح مختبر الإعادة التاريخية
Trading Academy|أكاديمية التداول
Open Academy|فتح الأكاديمية
Investor evidence|أدلة المستثمر
Review evidence|مراجعة الأدلة
Integration status|حالة التكامل
View audit|عرض التدقيق
Assessment history|تاريخ التقييم
Created|تاريخ الإنشاء
Foundation|الأساس
Modeled allocation|التخصيص النموذجي
Status|الحالة
Details|التفاصيل
Saved market replays|المحاكاة المحفوظة
Scenario|السيناريو
Step|الخطوة
Virtual equity|القيمة الافتراضية
Continue|متابعة
Activity journal|سجل النشاط
Privacy and data controls|الخصوصية والتحكم في البيانات
Export my data|تصدير بياناتي
Delete account|حذف الحساب
Investor workspace|مساحة المستثمر
← Investor workspace|← مساحة المستثمر
Investor dashboard|لوحة المستثمر
← Investor dashboard|← لوحة المستثمر
Dashboard|لوحة التحكم
Live-input assessment|تقييم المدخلات المباشرة
01 · Initial financial intake|01 · البيانات المالية الأولية
Start adaptive assessment →|بدء التقييم التكيفي ←
Unsure — stop assessment|غير متأكد — إيقاف التقييم
Assessment paused|تم إيقاف التقييم مؤقتاً
Resume|استئناف
Initial candidate|مرشح أولي
Unresolved candidate|مرشح غير محسوم
04 · Structured profile|04 · ملف المستثمر المنظم
Load remaining fictional example fields|تحميل بقية حقول المثال الافتراضي
Financial goals|الأهداف المالية
Calculate conditional plan|حساب الخطة المشروطة
Restart|إعادة البدء
Goal ID|معرف الهدف
Inflation-adjusted target|هدف معدل بالتضخم
Calculated conditional plan|الخطة المشروطة المحسوبة
Export calculated JSON|تصدير نتائج JSON
New assessment|تقييم جديد
05 · Explicit clarification|05 · توضيح صريح
Confirm and calculate|تأكيد وحساب
Reject / restart|رفض / إعادة البدء
Plan not released|لم يتم إصدار الخطة
Strategy Backtesting|اختبار الاستراتيجيات
Experiment setup|إعداد التجربة
Equity proxy|نموذج السهم
Strategy|الاستراتيجية
Initial virtual capital (EGP)|رأس المال الافتراضي الأولي (جنيه)
Entry allocation (%)|تخصيص الدخول (%)
Position stop (%) · 0 disables|وقف خسارة المركز (%) · صفر للتعطيل
Portfolio drawdown lock (%) · 0 disables|حد تراجع المحفظة (%) · صفر للتعطيل
Transaction fee (bps)|رسوم المعاملة (نقطة أساس)
Normal half-spread (bps)|نصف الفارق الطبيعي (نقطة أساس)
Stress half-spread (bps)|نصف الفارق وقت الضغط (نقطة أساس)
Extra slippage (bps)|انزلاق إضافي (نقطة أساس)
Run experiment|تشغيل التجربة
Check actual historical eligibility|التحقق من أهلية التاريخ الفعلي
Performance comparison|مقارنة الأداء
Order journal|سجل الأوامر
Submitted|تم الإرسال
Executed|تم التنفيذ
Side|الاتجاه
Units|الوحدات
Price|السعر
Fee|الرسوم
Reason|السبب
Decision timeline|التسلسل الزمني للقرارات
Action|الإجراء
Equity|قيمة المحفظة
Locked strategy coverage|تغطية الاستراتيجيات المقفلة
Rule / gap|القاعدة / الفجوة
Search instrument|بحث عن أصل
Instrument|الأصل
Historical cutoff (optional)|تاريخ القطع التاريخي (اختياري)
Analyze|تحليل
Select instrument|اختر الأصل
Calculated indicators|المؤشرات المحسوبة
Comparable peers|النظراء المتوافقون
Financial statement evidence|أدلة القوائم المالية
Fund characteristics and NAV samples|خصائص الصندوق وعينات صافي القيمة
Cash dividend events|أحداث التوزيعات النقدية
Scenario laboratory|مختبر السيناريوهات
Model|النموذج
Calculate scenario|حساب السيناريو
Search catalogue|بحث في الدليل
Data mode|وضع البيانات
Observed samples (retrospective)|عينات مرصودة (بأثر رجعي)
My replay — current step|محاكاتي — الخطوة الحالية
D5 intraday exercise|تمرين لحظي اصطناعي D5
Observation cutoff (optional)|تاريخ القطع (اختياري)
Saved replay|المحاكاة المحفوظة
Intraday anchor|مرجع الجلسة اللحظية
Exercise step (0–23)|خطوة التمرين (0–23)
Refresh|تحديث
Market context & evidence|سياق السوق والأدلة
Mode|الوضع
Historical evidence|أدلة تاريخية
Saved synthetic replay|محاكاة اصطناعية محفوظة
Available by|متاح حتى
Starting virtual EGP|رأس المال الافتراضي بالجنيه
Evaluation exposure|كشف بيانات التقييم
Allow validation/test scenarios|السماح بسيناريوهات التحقق والاختبار
Start replay|بدء المحاكاة
Advance one step →|تقدم خطوة واحدة ←
Export session JSON|تصدير الجلسة JSON
Investment universe|عالم الاستثمارات
Queue buy|إرسال شراء معلق
Queue sell|إرسال بيع معلق
Cancel pending|إلغاء المعلق
Virtual portfolio|محفظة افتراضية
Mark|سعر التقييم
Value|القيمة
Execution journal|سجل التنفيذ
Order|الأمر
Live simulated tape|شريط السوق المحاكى
Historical context|السياق التاريخي
Economic context|السياق الاقتصادي
Leverage stress lab|مختبر ضغط الرافعة المالية
Capital|رأس المال
Exposure multiple|مضاعف التعرض
Asset shock %|صدمة الأصل %
Calculate|حساب
Historical evidence browser — read only|متصفح الأدلة التاريخية — للقراءة فقط
As-of date|التاريخ المرجعي
Load available reports|تحميل التقارير المتاحة
Selected instrument: retrospective source samples|الأصل المحدد: عينات مصدر بأثر رجعي
Load selected instrument samples|تحميل عينات الأصل المحدد
Environment|البيئة
Observed ADIB + EGX30 (D1 candidate)|ADIB وEGX30 مرصودان (D1 مرشح)
Extended synthetic paths (D5)|مسارات اصطناعية ممتدة (D5)
Intervals|الفترات
Previous|السابق
Next observation|المشاهدة التالية
Reset|إعادة ضبط
Observed price history · 51 shared dates|تاريخ السعر المرصود · 51 تاريخاً مشتركاً
Information available by this date|المعلومات المتاحة حتى هذا التاريخ
Company and global events|أحداث الشركات والعالم
Latest economic vintages|أحدث إصدارات البيانات الاقتصادية
Verification gate|بوابة التحقق
ADIB 20-interval candidate paper experiment|تجربة ورقية مرشحة لـ ADIB خلال 20 فترة
Run candidate experiment|تشغيل التجربة المرشحة
Extended D5 training environment|بيئة تدريب اصطناعية ممتدة D5
Integer Portfolio Optimization|تحسين المحفظة بأعداد صحيحة
Decision model|نموذج القرار
Instrument 1|الأصل 1
Instrument 2 (optional)|الأصل 2 (اختياري)
Instrument 3 (optional)|الأصل 3 (اختياري)
Starting units 1|الوحدات الابتدائية 1
Starting units 2|الوحدات الابتدائية 2
Starting units 3|الوحدات الابتدائية 3
Initial available cash (virtual EGP)|النقد المتاح الأولي (جنيه افتراضي)
Forecast horizon (1–20 steps)|أفق التوقع (1–20 خطوة)
Downside penalty λ|عقوبة المخاطر السلبية λ
Cash reserve %|الاحتياطي النقدي %
Single asset cap %|حد الأصل الواحد %
Total exposure cap %|حد التعرض الكلي %
Per-step turnover cap %|حد الدوران لكل خطوة %
CVaR confidence (0.50–0.99)|مستوى ثقة CVaR (0.50–0.99)
Commission (bps)|العمولة (نقطة أساس)
Half spread + slippage (bps)|نصف الفارق + الانزلاق (نقطة أساس)
Optimize and replay|تحسين ومحاكاة
Performance|الأداء
Solver decisions|قرارات المحلّل
Buy units|وحدات الشراء
Sell units|وحدات البيع
Expected return %|العائد المتوقع %
CVaR loss %|خسارة CVaR %
Equity EGP|قيمة المحفظة بالجنيه
Next-step execution|تنفيذ الخطوة التالية
Buy|شراء
Sell|بيع
Cost EGP|التكلفة بالجنيه
Learning progress|تقدم التعلم
Curriculum by strategy|المنهج حسب الاستراتيجية
Example|مثال
Practice|تدريب
Investor evidence journal|سجل أدلة المستثمر
Replay activity|نشاط المحاكاة
Buys|عمليات الشراء
Sells|عمليات البيع
Rejected|المرفوضة
Holdings|الحيازات
Return %|العائد %
Drawdown %|التراجع %
Phase 19 · Implementation audit|المرحلة 19 · تدقيق التنفيذ
Filter status|تصفية الحالة
All|الكل
implemented|منفذ
partial|جزئي
blocked|متوقف
 deferred_v2|مؤجل إلى V2
Work item|بند العمل
Implementation|التنفيذ
Evidence|الأدلة
Remaining gap|الفجوة المتبقية
Augmented Trading|التداول المعزز
Investor Intelligence|ذكاء المستثمر
Monthly income|الدخل الشهري
monthly income|الدخل الشهري
monthly expenses|المصروفات الشهرية
monthly debt payment|القسط الشهري للدين
debt principal|أصل الدين
debt annual rate|معدل الفائدة السنوية للدين
investment savings|مدخرات الاستثمار
earmarked savings|مدخرات مخصصة
emergency reserve separate|احتياطي طوارئ منفصل
invested from savings|المستثمر من المدخرات
primary goal weight|وزن الهدف الأساسي
debt overdue|دين متأخر
Yes|نعم
No|لا
Cancel|إلغاء
Close|إغلاق
Search|بحث
No data|لا توجد بيانات
Insufficient data|بيانات غير كافية
Historical candidate|تاريخ مرشح
D5 synthetic|D5 اصطناعي
hold|احتفاظ
filled|تم التنفيذ
rejected|مرفوض
optimal|حل أمثل
infeasible|غير قابل للتحقيق
not_optimal|لم يثبت الحل الأمثل
not_implemented|غير منفذ
synthetic_proxy|نموذج اصطناعي
Source|المصدر
'''
translations={k.strip():v.strip() for k,v in (l.split('|',1) for l in labels.splitlines() if '|' in l)}
extra_labels='''Assessment versions|إصدارات التقييم
Virtual market replays|محاكاة السوق الافتراضية
Authorized live allocation|التخصيص الفعلي المصرح به
No live trading integration|لا يوجد ربط تداول فعلي
YOUR LOCAL INVESTOR WORKSPACE|مساحة المستثمر المحلية
Use an alias, not your real name. No external identity provider or brokerage connection.|استخدم اسماً مستعاراً وليس اسمك الحقيقي. لا يوجد مزود هوية خارجي أو اتصال بالوسيط.
Profile contents are encrypted on disk. Forgotten passwords cannot be recovered. This is a local engineering prototype; test with fictional data until security review.|محتويات الملف مشفرة على الجهاز. لا يمكن استعادة كلمات المرور المنسية. هذا نموذج هندسي محلي؛ اختبر ببيانات افتراضية حتى مراجعة الأمان.
Save your assessment and market replay decisions under a single private account. All investment allocations are conditional and all orders are virtual.|احفظ تقييمك وقرارات المحاكاة في حساب خاص واحد. جميع التخصيصات مشروطة وكل الأوامر افتراضية.
Review source-linked financial statements, fund characteristics and hypothetical valuation scenarios.|راجع القوائم المالية المرتبطة بالمصادر وخصائص الصناديق وسيناريوهات التقييم الافتراضية.
Explore price indicators, candlesticks and chronological replay signals.|استكشف المؤشرات السعرية والشموع والإشارات الزمنية في المحاكاة.
Explore dated news, macro releases, sector breadth and evidence conflicts.|استكشف الأخبار المؤرخة والتقارير الاقتصادية واتساع القطاعات وتعارض الأدلة.
Run synthetic strategy experiments with next-step execution and cost controls.|شغّل تجارب استراتيجيات اصطناعية مع تنفيذ الخطوة التالية وضبط التكاليف.
Scenario-based integer allocation, costs, cash limits and downside-risk optimization (D5).|تخصيص بالأعداد الصحيحة وفق السيناريوهات والتكاليف وحدود النقد وتحسين المخاطر السلبية (D5).
Chronological observed ADIB and EGX30 sample, evidence gates and extended synthetic sessions.|عينة ADIB وEGX30 المرصودة زمنياً وبوابات التحقق والجلسات الاصطناعية الممتدة.
31 lessons with server-graded quizzes and encrypted saved progress.|31 درساً باختبارات تُصحح محلياً وتقدم محفوظ مشفر.
Review saved learning and simulated trading activity. No automated personality inference.|راجع التعلم المحفوظ ونشاط التداول المحاكى. لا استنتاج تلقائي للشخصية.
No completed assessments.|لا توجد تقييمات مكتملة.
No saved virtual replays.|لا توجد محاكاة افتراضية محفوظة.
No activity yet.|لا يوجد نشاط بعد.
Resume assessment|استئناف التقييم
View|عرض
Review|مراجعة
Foundation|الأساس
Portfolio|المحفظة
Investment|الاستثمار
Trading|التداول
Hybrid|مختلط
Financial readiness|الجاهزية المالية
Cash flow and liquidity|التدفق النقدي والسيولة
Financial goals and inflation|الأهداف المالية والتضخم
Risk capacity and loss budgets|القدرة على تحمل المخاطر وميزانية الخسائر
Returns, costs and compounding|العوائد والتكاليف والتركيب
Market mechanics and orders|آليات السوق والأوامر
Evidence and independent judgment|الأدلة والحكم المستقل
Behavior, discipline and stress|السلوك والانضباط والضغط
Diversification and concentration|التنويع والتركيز
Index funds and tracking|صناديق المؤشرات والتتبع
Managed and balanced funds|الصناديق المدارة والمتوازنة
Asset allocation and rebalancing|تخصيص الأصول وإعادة التوازن
Financial statements|القوائم المالية
Valuation and margin of safety|التقييم وهامش الأمان
Growth and GARP|النمو بسعر معقول
Quality and defensive analysis|الجودة والتحليل الدفاعي
Dividend sustainability and growth|استدامة التوزيعات ونموها
Long-horizon thesis and review|فرضية الاستثمار طويل الأجل والمراجعة
Charts and market regimes|الرسوم وحالات السوق
Position and swing horizons|آفاق تداول المراكز والتداول المتأرجح
Position sizing and execution risk|حجم المركز ومخاطر التنفيذ
Trend following and momentum|اتباع الاتجاه والزخم
Breakout and pullback|الاختراق والتصحيح
Range and mean reversion|النطاق والارتداد إلى المتوسط
Reversal and relative strength|الانعكاس والقوة النسبية
Event-driven decisions|القرارات القائمة على الأحداث
Intraday and scalping constraints|قيود التداول اليومي والمضاربة السريعة
Backtesting and trade journal|اختبار الاستراتيجيات وسجل التداول
Income planning and cash reserves|تخطيط الدخل والاحتياطيات النقدية
Core-satellite and separate mandates|المحفظة الأساسية والفرعية والمهام المنفصلة
Market adaptive mandates|مهام التكيف مع السوق
Ending equity|قيمة المحفظة النهائية
Strategy return|عائد الاستراتيجية
Optimizer return|عائد المحسّن
Passive return|العائد السلبي
Buy & hold return|عائد الشراء والاحتفاظ
EGX30 gross factor|عائد EGX30 الإجمالي
Costs|التكاليف
Max drawdown|أقصى تراجع
D5 synthetic experiments only. No verified historical backtests, live orders or strategy recommendations. Evaluation scenarios require explicit exposure consent.|تجارب اصطناعية D5 فقط. لا توجد اختبارات تاريخية متحققة أو أوامر فعلية أو توصيات. تتطلب سيناريوهات التقييم موافقة صريحة على كشف النتائج.
Explicitly expose held-out evaluation outcomes|الموافقة على كشف نتائج التقييم المعزولة
Explicitly expose evaluation scenario outcomes|الموافقة على كشف نتائج سيناريو التقييم
I understand this reveals the evaluation interval and is not verified historical performance.|أفهم أن ذلك يكشف فترة التقييم وليس أداءً تاريخياً متحققاً.
Account created. Sign in using your password.|تم إنشاء الحساب. سجّل الدخول بكلمة المرور.
Invalid credentials|بيانات دخول غير صحيحة
Sign in required|يلزم تسجيل الدخول
'''
translations.update(dict(l.split('|',1) for l in extra_labels.splitlines() if '|' in l))
for e in entries:translations.setdefault(e['en'],e['ar']);translations.setdefault(e['id'],e['ar'] if e['group']!='strategy' else e['id'])
# Metric IDs are preserved in raw exports; translate displayed label only.
for e in entries:
    if e['group']=='metric':translations.setdefault(e['id'].replace('_',' '),e['ar'])
# preserve canonical strategy IDs, translated displayed names
assert len({e['id'] for e in entries})==len(entries)
data={'entries':entries,'translations':translations,'notice':{'en':'Arabic interface labels and help are available. Some original evidence, lesson text, question prompts and diagnostic messages remain in English. No live trading.','ar':'تتوفر عناوين الواجهة والمساعدة بالعربية. قد تبقى بعض الأدلة والدروس والأسئلة ورسائل التشخيص الأصلية بالإنجليزية. لا تداول فعلي.'}}
(OUT/'help_catalogue.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));(OUT/'mobile-catalogue.js').write_text('window.MOBILE_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
print('entries',len(entries),'groups',{g:sum(e['group']==g for e in entries) for g in ['strategy','metric','tool']},'labels',len(translations))

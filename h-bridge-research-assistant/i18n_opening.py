"""연령·생애주기·성별 맞춤 첫 인사·placeholder — ko 외 언어 확장."""

from __future__ import annotations

# LIFE_STAGE_OPTIONS · AGE_GROUPS 라벨은 한국어 유지 → 키 슬러그 동일
OPENING_I18N: dict[str, dict[str, str]] = {
    "en": {
        "opening": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "Through our dialogue, we'll look for the treasures hidden in your life.\n\n"
            "What story is taking up the most space in your heart today? "
            "Even a small piece of daily life is welcome.\n\n"
            "We're listening."
        ),
        "opening_stage_초등학생": (
            "Hi! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll look for treasures in your heart through our chat. "
            "School, friends, home—or whatever felt exciting or hard lately—all count.\n\n"
            "What's the first story that comes to mind today?"
        ),
        "opening_stage_중학생": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll explore the stories in your life together. "
            "Friends, school, dreams, and little everyday moments are all precious pieces.\n\n"
            "Share whatever is staying with you right now."
        ),
        "opening_stage_고등학생": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll continue the stories you care about. "
            "Future paths, relationships, worries, or small joys—all are welcome.\n\n"
            "What story feels largest in your heart today?"
        ),
        "opening_stage_대학생": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll weave the pieces of your life together through dialogue. "
            "Studies, relationships, choices ahead—write without pressure.\n\n"
            "What's on your mind right now?"
        ),
        "opening_stage_성인일반": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "Through our dialogue, we'll look for the treasures hidden in your life.\n\n"
            "What story is taking up the most space in your heart today? "
            "Even a small piece of daily life is welcome.\n\n"
            "We're listening."
        ),
        "opening_stage_은퇴_후_삶": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll gently revisit the stories you've lived and the heart you carry now. "
            "Memories, relationships, feelings—anything is welcome.\n\n"
            "Share at your own pace."
        ),
        "opening_age_10대": (
            "Hi! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll explore your days and inner stories together. "
            "Friends, school, small joys or hurts—all count.\n\n"
            "What comes to mind first right now?"
        ),
        "opening_age_20대": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll walk the path you've taken and the heart you hold now. "
            "Choices, relationships, and small daily moments all matter.\n\n"
            "What story feels largest today?"
        ),
        "opening_age_30대": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll look for hidden treasures in work and relationships. "
            "A small scene from a busy day is enough.\n\n"
            "What's on your mind?"
        ),
        "opening_age_40대": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll sit with the weight of life and its bright moments together. "
            "Responsibility, transition, small joys—anything goes.\n\n"
            "We're listening."
        ),
        "opening_age_50대": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll reflect on the stories you've built and how you feel now.\n\n"
            "What would you like to share today?"
        ),
        "opening_age_60대_이상": (
            "Hello! I'm **dlinso**, your Mind Gardener.\n\n"
            "We'll move slowly through life's memories and today's heart. "
            "Even a small daily moment is precious.\n\n"
            "Share comfortably, in your own time."
        ),
        "opening_gender_note_여": (
            "Write in whatever tone feels natural—there's no rush."
        ),
        "opening_gender_note_남": (
            "No pressure—start with any scene that surfaced today."
        ),
        "opening_gender_note_기타": (
            "Any words are welcome. Tell your story at your own pace."
        ),
        "chat_opening_placeholder": (
            "What story is sitting largest in your heart today?"
        ),
        "chat_opening_placeholder_stage_초등학생": (
            "What's the first story you think of today?"
        ),
        "chat_opening_placeholder_stage_중학생": (
            "What's staying with you right now?"
        ),
        "chat_opening_placeholder_stage_고등학생": (
            "What story feels largest today?"
        ),
        "chat_opening_placeholder_stage_대학생": (
            "What's on your mind right now?"
        ),
        "chat_opening_placeholder_age_10대": "What comes to mind first?",
        "chat_opening_placeholder_age_20대": "Share what's on your heart today…",
        "chat_opening_placeholder_age_30대": "What's on your mind right now?",
        "chat_opening_placeholder_age_40대": "What would you like to share today?",
        "chat_opening_placeholder_age_50대": "Share your story comfortably…",
        "chat_opening_placeholder_age_60대_이상": (
            "Slowly, share today's story…"
        ),
    },
    "mn": {
        "opening": (
            "Сайн уу! Би **dlinso**, таны **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Яриагаар амьдралынхаа нууц эрдэнэсийг хамтдаа олно.\n\n"
            "Өнөөдөр зүрхэнд хамгийн том байрлаж буй түүх юу вэ? "
            "Жижиг өдөр тутмын зүйл ч болно.\n\n"
            "Ярьж өгнө үү."
        ),
        "opening_stage_초등학생": (
            "Сайн уу! Би **dlinso**, чиний **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Сургууль, найз, гэр—сүүлийн баярлах эсвэл уйтгартай зүйл ч болно.\n\n"
            "Өнөөдөр эхлээд санаанд орж ирсэн түүхээ хэлээрэй."
        ),
        "opening_stage_중학생": (
            "Сайн уу! Би **dlinso**, чиний **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Найз, сургууль, мөрөөдөл, жижиг өдөр тутам—бүгд үнэтэй.\n\n"
            "Одоо зүрхэнд үлдсэн түүхээ бичээрэй."
        ),
        "opening_stage_고등학생": (
            "Сайн уу! Би **dlinso**, чиний **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Ирээдүй, харилцаа, санаа зоволт, баяр бүхий зүйл зөвшөөрөгдөнө.\n\n"
            "Өнөөдрийн хамгийн том түүхээ хуваалцаарай."
        ),
        "opening_stage_대학생": (
            "Сайн уу! Би **dlinso**, чиний **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Сурлага, харилцаа, сонголт—ачаалгүй бичээрэй.\n\n"
            "Одоо санаанд байгаа түүхээ хэлээрэй."
        ),
        "opening_stage_성인일반": (
            "Сайн уу! Би **dlinso**, таны **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Яриагаар амьдралынхаа эрдэнэсийг хамтдаа олно.\n\n"
            "Өнөөдөр зүрхэнд хамгийн том түүх юу вэ?\n\n"
            "Ярьж өгнө үү."
        ),
        "opening_stage_은퇴_후_삶": (
            "Сайн уу! Би **dlinso**, таны **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Өнгөрсөн түүх, одоогийн сэтгэлийг аажмаар хамтдаа үзнэ.\n\n"
            "Өөрийн хурдаар ярьж өгнө үү."
        ),
        "opening_age_10대": (
            "Сайн уу! Би **dlinso**, чиний **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Найз, сургууль, баяр эсвэл гуниг—бүгд болно.\n\n"
            "Эхлээд санаанд орсон зүйлээ хэлээрэй."
        ),
        "opening_age_20대": (
            "Сайн уу! Би **dlinso**, чиний **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Сонголт, харилцаа, өдөр тутмын зүйл бүхэн чухал.\n\n"
            "Өнөөдрийн түүхээ хуваалцаарай."
        ),
        "opening_age_30대": (
            "Сайн уу! Би **dlinso**, таны **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Ажил, харилцааны доторх эрдэнэсийг хамтдаа олно.\n\n"
            "Одоо юу бодож байна вэ?"
        ),
        "opening_age_40대": (
            "Сайн уу! Би **dlinso**, таны **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Амьдралын жин, гэрэл гэгээтэй мөчүүдийг хамтдаа үзнэ.\n\n"
            "Түүхээ хуваалцаарай."
        ),
        "opening_age_50대": (
            "Сайн уу! Би **dlinso**, таны **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Хуримтлуулсан түүх, одоогийн сэтгэлийг хамтдаа үзнэ.\n\n"
            "Өнөөдөр юу хэлмээр байна?"
        ),
        "opening_age_60대_이상": (
            "Сайн уу! Би **dlinso**, таны **Сэтгэлийн цэцэрлэгчин**.\n\n"
            "Дурсамж, өнөөдрийн зүрхийг аажмаар үргэлжлүүлнэ.\n\n"
            "Тайвшлан ярьж өгнө үү."
        ),
        "opening_gender_note_여": "Тайвшлан, өөрийн хурдаар бичээрэй.",
        "opening_gender_note_남": "Ачаагүй, өнөөдөр санаанд орсон зүйлээс эхэлж болно.",
        "opening_gender_note_기타": "Ямар ч үг зөв. Өөрийн хурдаар ярьна уу.",
        "chat_opening_placeholder": "Өнөөдөр зүрхэнд хамгийн том түүх юу вэ?",
        "chat_opening_placeholder_stage_초등학생": "Эхлээд санаанд орсон түүхээ бичээрэй.",
        "chat_opening_placeholder_stage_중학생": "Одоо зүрхэнд үлдсэн түүх…",
        "chat_opening_placeholder_stage_고등학생": "Өнөөдрийн хамгийн том түүх…",
        "chat_opening_placeholder_stage_대학생": "Одоо санаанд байгаа түүх…",
        "chat_opening_placeholder_age_10대": "Эхлээд санаанд орсон зүйл?",
        "chat_opening_placeholder_age_20대": "Өнөөдрийн түүхээ бичээрэй…",
        "chat_opening_placeholder_age_30대": "Одоо юу бодож байна…",
        "chat_opening_placeholder_age_40대": "Өнөөдөр юу хэлмээр байна…",
        "chat_opening_placeholder_age_50대": "Тайвшлан түүхээ бичээрэй…",
        "chat_opening_placeholder_age_60대_이상": "Аажмаар, өнөөдрийн түүх…",
    },
    "ja": {
        "opening": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "対話を通して、あなたの人生に隠れた宝物を一緒に探します。\n\n"
            "今日、心いちばんに残っている物語は何ですか？"
            "小さな日常の一片でも大丈夫です。\n\n"
            "お聞かせください。"
        ),
        "opening_stage_초등학생": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "学校・友だち・おうちのこと、うれしかったことやつらかったことも大歓迎。\n\n"
            "いちばん先に浮かんだ話を聞かせてくれる？"
        ),
        "opening_stage_중학생": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "友だち、学校、夢、小さな日常も大切なかけらです。\n\n"
            "今、心に残っている話を気軽に書いてください。"
        ),
        "opening_stage_고등학생": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "進路、関係、いまの悩みや小さなよろこびも大丈夫です。\n\n"
            "今日いちばん大きく残っている物語を聞かせてください。"
        ),
        "opening_stage_대학생": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "専攻、関係、これからの選択—無理なく書いてください。\n\n"
            "いま心にある話を聞かせてください。"
        ),
        "opening_stage_성인일반": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "対話を通して、人生の中の宝物を一緒に探します。\n\n"
            "今日、心いちばんに残っている物語は何ですか？\n\n"
            "お聞かせください。"
        ),
        "opening_stage_은퇴_후_삶": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "これまでの物語と、いまの心をゆっくり一緒にたどります。\n\n"
            "ご自身のペースでお話しください。"
        ),
        "opening_age_10대": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "友だち、学校、小さなよろこびやつらさも大丈夫。\n\n"
            "いちばん先に浮かんだ話を聞かせてくれる？"
        ),
        "opening_age_20대": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "歩いてきた道といまの心を、対話でつなぎます。\n\n"
            "今日いちばん大きな物語を聞かせてください。"
        ),
        "opening_age_30대": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "仕事と関係の中の宝物を一緒に探します。忙しい一日の小さな場面でも。\n\n"
            "いま心にある話をどうぞ。"
        ),
        "opening_age_40대": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "人生の重さと光る瞬間を一緒に味わいます。\n\n"
            "お聞かせください。"
        ),
        "opening_age_50대": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "積み重ねた物語といまの心を一緒に見つめます。\n\n"
            "今日伝えたい話をどうぞ。"
        ),
        "opening_age_60대_이상": (
            "こんにちは。**心の庭師** dlinso です。\n\n"
            "ゆっくり、記憶といまの心をつなぎます。小さな日常も大切です。\n\n"
            "安心してお話しください。"
        ),
        "opening_gender_note_여": "無理のない口調で、ゆっくり書いてください。",
        "opening_gender_note_남": "気楽に、今日浮かんだ場面からで大丈夫です。",
        "opening_gender_note_기타": "どんな表現でも歓迎です。あなたのペースで。",
        "chat_opening_placeholder": "今日、心いちばんに残っている物語は？",
        "chat_opening_placeholder_stage_초등학생": "いちばん先に浮かんだ話を書いてみて。",
        "chat_opening_placeholder_stage_중학생": "今、心に残っている話…",
        "chat_opening_placeholder_stage_고등학생": "今日いちばん大きな物語…",
        "chat_opening_placeholder_stage_대학생": "いま心にある話…",
        "chat_opening_placeholder_age_10대": "いちばん先に浮かんだ話は？",
        "chat_opening_placeholder_age_20대": "今日の心の話を…",
        "chat_opening_placeholder_age_30대": "いま心にある話…",
        "chat_opening_placeholder_age_40대": "今日伝えたい話…",
        "chat_opening_placeholder_age_50대": "気楽に物語を…",
        "chat_opening_placeholder_age_60대_이상": "ゆっくり、今日の物語…",
    },
    "zh": {
        "opening": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "我们将通过对谈，一起寻找你生命中隐藏的宝藏。\n\n"
            "今天，心里占最大位置的故事是什么？"
            "日常的一小片也可以。\n\n"
            "请慢慢说给我们听。"
        ),
        "opening_stage_초등학생": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "学校、朋友、家里的事，最近开心或难过的事都可以。\n\n"
            "今天最先想到的故事是什么？"
        ),
        "opening_stage_중학생": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "朋友、学校、梦想、小小的日常都是珍贵的碎片。\n\n"
            "请写下此刻心里最放不下的事。"
        ),
        "opening_stage_고등학생": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "升学、关系、现在的烦恼或小快乐都可以。\n\n"
            "今天心里最大的故事是什么？"
        ),
        "opening_stage_대학생": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "专业、关系、未来的选择——不必有压力，写下来就好。\n\n"
            "此刻心里的事，请告诉我们。"
        ),
        "opening_stage_성인일반": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "我们将通过对谈，一起寻找你生命中的宝藏。\n\n"
            "今天心里最大的故事是什么？\n\n"
            "我们在这里倾听。"
        ),
        "opening_stage_은퇴_후_삶": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "我们会慢慢梳理走过的路与此刻的心。\n\n"
            "请按自己的节奏分享。"
        ),
        "opening_age_10대": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "朋友、学校、小小的快乐或难过都可以。\n\n"
            "此刻最先想到的是什么？"
        ),
        "opening_age_20대": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "我们一起连接你走过的路与现在的心。\n\n"
            "今天最想分享的故事是什么？"
        ),
        "opening_age_30대": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "在工作与关系里寻找隐藏的宝藏，忙碌一天里的小场景也可以。\n\n"
            "此刻心里的事请告诉我们。"
        ),
        "opening_age_40대": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "我们一起面对生命的重量与闪亮的瞬间。\n\n"
            "请分享你的故事。"
        ),
        "opening_age_50대": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "我们一起回看积累的故事与现在的心情。\n\n"
            "今天最想说什么？"
        ),
        "opening_age_60대_이상": (
            "你好！我是 **dlinso**，你的**心灵园丁**。\n\n"
            "慢慢连接生命的记忆与今天的心，日常的一小片也很珍贵。\n\n"
            "请安心分享。"
        ),
        "opening_gender_note_여": "用舒服的方式，慢慢写就好。",
        "opening_gender_note_남": "不必有压力，从今天浮现的画面开始也可以。",
        "opening_gender_note_기타": "任何表达都可以，请按你的节奏诉说。",
        "chat_opening_placeholder": "今天心里最大的故事是什么？",
        "chat_opening_placeholder_stage_초등학생": "最先想到的故事是什么？",
        "chat_opening_placeholder_stage_중학생": "此刻心里放不下的事…",
        "chat_opening_placeholder_stage_고등학생": "今天心里最大的故事…",
        "chat_opening_placeholder_stage_대학생": "此刻心里的事…",
        "chat_opening_placeholder_age_10대": "最先想到的是什么？",
        "chat_opening_placeholder_age_20대": "分享今天心里的故事…",
        "chat_opening_placeholder_age_30대": "此刻心里的事…",
        "chat_opening_placeholder_age_40대": "今天想分享的故事…",
        "chat_opening_placeholder_age_50대": "轻松地写下故事…",
        "chat_opening_placeholder_age_60대_이상": "慢慢写下今天的故事…",
    },
    "vi": {
        "opening": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Qua đối thoại, chúng ta sẽ cùng tìm những kho báu ẩn trong đời bạn.\n\n"
            "Hôm nay, câu chuyện nào chiếm chỗ lớn nhất trong tim bạn? "
            "Một mảnh nhỏ trong ngày cũng được.\n\n"
            "Hãy kể cho chúng tôi nghe."
        ),
        "opening_stage_초등학생": (
            "Chào bạn! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Trường, bạn bè, nhà—điều vui hay buồn gần đây đều được.\n\n"
            "Câu chuyện đầu tiên nghĩ đến hôm nay là gì?"
        ),
        "opening_stage_중학생": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Bạn bè, trường học, ước mơ, khoảnh khắc nhỏ đều quý.\n\n"
            "Hãy viết điều còn lưu lại trong tim lúc này."
        ),
        "opening_stage_고등학생": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Định hướng, quan hệ, lo lắng hay niềm vui nhỏ—đều được.\n\n"
            "Câu chuyện lớn nhất hôm nay là gì?"
        ),
        "opening_stage_대학생": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Chuyên ngành, quan hệ, lựa chọn phía trước—viết thoải mái.\n\n"
            "Điều gì đang ở trong tim bạn?"
        ),
        "opening_stage_성인일반": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Chúng ta sẽ cùng tìm kho báu trong đời bạn qua đối thoại.\n\n"
            "Hôm nay câu chuyện lớn nhất trong tim là gì?\n\n"
            "Chúng tôi đang lắng nghe."
        ),
        "opening_stage_은퇴_후_삶": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Chúng ta sẽ nhẹ nhàng nhìn lại quãng đời đã qua và trái tim hiện tại.\n\n"
            "Hãy kể theo nhịp của bạn."
        ),
        "opening_age_10대": (
            "Chào bạn! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Bạn bè, trường, niềm vui hay buồn nhỏ—đều được.\n\n"
            "Điều gì nghĩ đến đầu tiên lúc này?"
        ),
        "opening_age_20대": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Chúng ta nối con đường bạn đã đi với trái tim hiện tại.\n\n"
            "Câu chuyện lớn nhất hôm nay là gì?"
        ),
        "opening_age_30대": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Cùng tìm kho báu trong công việc và quan hệ—một cảnh nhỏ trong ngày bận cũng đủ.\n\n"
            "Tim bạn đang nghĩ gì?"
        ),
        "opening_age_40대": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Chúng ta cùng nhìn gánh nặng và khoảnh sáng của đời.\n\n"
            "Hãy kể câu chuyện của bạn."
        ),
        "opening_age_50대": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Chúng ta cùng nhìn những gì đã tích lũy và cảm xúc hiện tại.\n\n"
            "Hôm nay bạn muốn chia sẻ điều gì?"
        ),
        "opening_age_60대_이상": (
            "Xin chào! Tôi là **dlinso**, **Người làm vườn tâm hồn** của bạn.\n\n"
            "Từ từ nối ký ức với trái tim hôm nay—một mảnh nhỏ cũng quý.\n\n"
            "Hãy kể một cách thoải mái."
        ),
        "opening_gender_note_여": "Viết theo giọng thoải mái, không vội.",
        "opening_gender_note_남": "Không áp lực—bắt đầu từ cảnh nghĩ đến hôm nay.",
        "opening_gender_note_기타": "Mọi cách diễn đạt đều được. Kể theo nhịp của bạn.",
        "chat_opening_placeholder": "Câu chuyện lớn nhất trong tim hôm nay?",
        "chat_opening_placeholder_stage_초등학생": "Câu chuyện nghĩ đến đầu tiên?",
        "chat_opening_placeholder_stage_중학생": "Điều còn lưu trong tim…",
        "chat_opening_placeholder_stage_고등학생": "Câu chuyện lớn nhất hôm nay…",
        "chat_opening_placeholder_stage_대학생": "Điều trong tim lúc này…",
        "chat_opening_placeholder_age_10대": "Nghĩ đến đầu tiên là gì?",
        "chat_opening_placeholder_age_20대": "Chia sẻ chuyện trong tim hôm nay…",
        "chat_opening_placeholder_age_30대": "Tim bạn đang nghĩ gì…",
        "chat_opening_placeholder_age_40대": "Muốn kể hôm nay…",
        "chat_opening_placeholder_age_50대": "Thoải mái kể câu chuyện…",
        "chat_opening_placeholder_age_60대_이상": "Từ từ, câu chuyện hôm nay…",
    },
}


def merge_opening_i18n(texts: dict[str, dict[str, str]]) -> None:
    """TEXTS dict에 맞춤 opening 키를 병합."""
    for lang, entries in OPENING_I18N.items():
        if lang in texts:
            texts[lang].update(entries)

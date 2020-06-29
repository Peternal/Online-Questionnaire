import datetime
import json

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now

from app.models import Questionnaire, Question, Option, Answer, Paper


# 转换问卷为字典
def serialize_questionnaire(questionnaire: Questionnaire):
    return {
        'id': questionnaire.id,
        'title': questionnaire.title,
        'description': questionnaire.description,
        'share': questionnaire.share,
        'limit': questionnaire.limit,
        'deadline': questionnaire.deadline.__str__(),
        'question': [{
            'id': q.id,
            'text': q.text,
            'kind': q.kind,
            'max_rate': q.max_rate,
            'conditional': q.conditional,
            'condition': q.condition_question,
            'condition_value': q.condition_value,
            'options': [{
                'id': opt.id,
                'text': opt.text,
            } for opt in q.option_set.all()]
        } for q in questionnaire.question_set.all()]
    }


# 主页
@login_required(login_url='/login')
def index_view(request):
    my_questionnaire = Questionnaire.objects.filter(creator=request.user).all()
    return render(request, "index.html", locals())


# 问卷设计处理函数
@login_required()
def design_view(request):
    if request.method == "GET":
        return render(request, "design.html")
    if request.method == "POST":
        form = json.loads(request.body)
        title = form.get("title")
        description = form.get("description")
        creator = request.user

        # 创建问卷
        questionnaire = Questionnaire.objects.create(
            title=title,
            description=description,
            creator=creator,
        )

        # 添加问卷的问题
        questions = []
        for question in form.get("question"):
            text = question['text']
            kind = question['kind']
            conditional = question.get("conditional") is not None
            condition = question.get('condition')
            condition_value = question.get('condition_value')
            max_rate = int(question.get("max", '0'))
            condition_opt = None
            if conditional:
                condition_question = questions[int(condition)]
                condition_opt = condition_question.option_set.all()[int(condition_value)].id

            q = Question.objects.create(
                questionnaire=questionnaire,
                text=text,
                kind=kind,
                max_rate=max_rate,
                conditional=conditional,
                condition_question=condition,
                condition_value=condition_opt,
            )
            # 如果是选择题添加选项
            if kind == "radio" or kind == "checkbox":
                for opt in question.get('options'):
                    q.option_set.add(Option.objects.create(question=q, text=opt['text']))
                q.save()
            questions.append(q)

        return JsonResponse({'id': questionnaire.id})


# 共享设置处理函数
def share_view(request, id):
    questionnaire = Questionnaire.objects.get(id=id)
    if request.method == "GET":
        return render(request, "share.html", locals())
    if request.method == "POST":
        form = request.POST
        questionnaire.share = form['share_way']
        questionnaire.limit = int(form['limit'])
        if form.get("deadline") is not None and len(form.get('deadline')) != 0:
            questionnaire.deadline = form.get('deadline')
        questionnaire.save()
        return render(request, "share.html", locals())


# 问卷填写视图
def paper_view(request, id):
    ip = request.META.get("REMOTE_ADDR"),
    ua = request.META.get('HTTP_USER_AGENT', 'unknown'),
    questionnaire = Questionnaire.objects.get(id=id)

    if questionnaire.deadline and questionnaire.deadline < now():
        message = "已过期"
        return render(request, "limited.html", locals())

    # 注册用户
    if questionnaire.share == "authorized":
        # 未登录
        if not request.user.is_authenticated:
            return redirect("/login")

    # 限制n次
    if questionnaire.share == "n":
        # 查询填写的份数
        if questionnaire.paper_set.count() >= questionnaire.limit:
            message = "超出填写限制"
            return render(request, "limited.html", locals())

    # 每天限制n次
    if questionnaire.share == "n-per-day":
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        # 查询今天填写的份数
        if questionnaire.paper_set.filter(date__range=(today_min, today_max)).count() >= questionnaire.limit:
            message = "超出单日填写限制"
            return render(request, "limited.html", locals())

    # 检查该IP和浏览器（User-Agent）是否已经填写过。
    if questionnaire.paper_set.filter(ip=ip, ua=ua).count() > 0:
        message = "你已填写过，无需重复填写"
        return render(request, "limited.html", locals())

    if request.method == 'GET':
        questionnaire_dict = serialize_questionnaire(questionnaire)
        questionnaire_json = json.dumps(questionnaire_dict)
        return render(request, "paper.html", locals())

    # 保存问卷答案
    if request.method == 'POST':
        form = json.loads(request.body)
        paper = Paper.objects.create(questionnaire=questionnaire, ip=ip, ua=ua)
        for answer in form.get("answers"):
            q = Question.objects.get(id=answer['question'])
            Answer.objects.create(paper=paper, question=q, answer=answer['answer'])
        return render(request, "thanks.html", locals())


def paper_dashboard_view(request, id):
    paper = Paper.objects.get(id=id)
    return render(request, "paper_dashboard.html", locals())


# 问卷详情页
def questionnaire_dashboard_view(request, id):
    questionnaire = Questionnaire.objects.get(id=id)
    papers = questionnaire.paper_set.all()
    first_paper = Paper.objects.filter(questionnaire=questionnaire).order_by('-date').first()
    last_paper = Paper.objects.filter(questionnaire=questionnaire).order_by('-date').last()

    question_set = questionnaire.question_set.all()
    for q in question_set:
        # 数值统计
        if q.kind in ["integer", "float"]:
            answers = Answer.objects.filter(paper__questionnaire=questionnaire, question=q).all()
            answers_values = [float(a.answer) for a in answers]
            if len(answers_values):
                q.max = max(answers_values)
                q.min = min(answers_values)
                q.total = sum(answers_values)
                q.avg = q.total / len(answers)

        if q.kind == "radio":
            q.opt_map = []
            total = Answer.objects.filter(question=q).count()
            if total != 0:
                for opt in Option.objects.filter(question=q).all():
                    c = Answer.objects.filter(answer=str(opt.id)).count()
                    q.opt_map.append({
                        'opt': opt,
                        'c': c,
                        'percent': c * 100 / total,
                    })

        if q.kind == "checkbox":
            q.opt_map = []
            total = Answer.objects.filter(question=q).count()
            if total != 0:
                for opt in Option.objects.filter(question=q).all():
                    c = Answer.objects.filter(answer__contains=str(opt.id)).count()
                    q.opt_map.append({
                        'opt': opt,
                        'c': c,
                        'percent': c * 100 / total,
                    })

    return render(request, "questionnaire_dashboard.html", locals())


# 登录处理
def login_view(request):
    if request.method == 'GET':
        return render(request, "login.html")
    if request.method == 'POST':
        form = request.POST
        username = form.get("username")
        password = form.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            return HttpResponse(""" <script>alert('用户名或密码错误'); window.history.back();</script>""")
        login(request, user)
        if request.GET.get("next"):
            redirect(request.GET.get("next"))
        return redirect("/")


# 注册处理函数
def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    if request.method == 'POST':
        form = request.POST
        username = form.get("username")
        password = form.get("password")
        password2 = form.get("password2")
        email = form.get("email")

        # 检查密码
        if password != password2:
            return HttpResponse(""" <script>alert('两次密码不一致'); window.history.back();</script>""")

        if len(password) < 6:
            return HttpResponse(""" <script>alert('密码至少6位'); window.history.back();</script>""")

        if User.objects.filter(username=username).count() != 0:
            return HttpResponse(""" <script>alert('用户名不可用'); window.history.back();</script>""")

        if User.objects.filter(email=email).count() != 0:
            return HttpResponse(""" <script>alert('邮箱不可用'); window.history.back();</script>""")

        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('/')


# 注销
def logout_view(request):
    logout(request)
    return redirect('/')


def questionnaire_delete_view(request, id):
    Questionnaire.objects.filter(id=id).delete()
    return redirect("/")


def paper_detail_view(request, id):
    paper = Paper.objects.get(id=id)
    return render(request, "paper_dashboard.html", locals())

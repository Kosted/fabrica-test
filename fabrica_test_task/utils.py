from interview.models import Interview, CompleteInterview, Answer
from users.models import AnonUser


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_by_token(request):
    request_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
    return AnonUser.objects.get(customtoken__key=request_token)


def get_answer_on_question_id(question_id, answers):
    for answer in answers:
        if answer.question.id == question_id:
            return answer


def pop_user_answer(question_id, user_answers):
    res = list()
    for i, answer in enumerate(user_answers):
        if answer['question_id'] == question_id:
            res.append(i)
    return tuple(user_answers.pop(i) for i in res[::-1])
    # return tuple(user_answers.pop(i) for i, answer in enumerate(dict_for_count) if answer['question_id'] == question_id)


def check_empty(answers: tuple):
    return tuple(answer['question_id'] for answer in answers if answer['answer'] == '')


def check_correct_variant(variants, variant_texts: tuple):
    return tuple(
        variant_text['question_id'] for variant_text in variant_texts if variant_text['answer'] not in [variant.text for variant in variants])

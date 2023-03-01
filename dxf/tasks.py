# -*- coding: utf-8 -*-
"""
@Auth ： 江宇旭
@Email ：jiang.yuxu@mech-mind.net
@Time ： 2023/3/1 17:13
"""
from time import sleep
from django.core.mail import send_mail
from celery import shared_task


@shared_task()
def send_feedback_email_task(subject, message):
    sleep(2)
    send_mail(
        subject=subject,
        message=message,
        from_email='377832421@qq.com',
        recipient_list=['jiang.yuxu@mech-mind.net'],
        fail_silently=False
    )

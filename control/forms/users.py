from flask import request
from flask_security import RegisterForm, ForgotPasswordForm, ResetPasswordForm, LoginForm
from flask_wtf import RecaptchaField

from control import app


class ExtendedRegisterForm(RegisterForm):
    recaptcha = RecaptchaField()


class ExtendedForgotPasswordForm(ForgotPasswordForm):
    recaptcha = RecaptchaField()


class ExtendedResetPasswordForm(ResetPasswordForm):
    recaptcha = RecaptchaField()


class ExtendedLoginForm(LoginForm):
    def validate(self):
        response = super(ExtendedLoginForm, self).validate()
        if response is False:
            error = ', '.join(['{}={}'.format(key, val) for key, val in self.errors.items()])
            form = ', '.join(['{}={}'.format(key, val) for key, val in request.form.items()])
            app.logger.warning('Loggin incorrect ({}, url={}, from={}, {})'.format(
                error, request.host_url, request.remote_addr, form))

        return response

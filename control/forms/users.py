from flask_security import RegisterForm, ForgotPasswordForm, ResetPasswordForm
from flask_wtf import RecaptchaField


class ExtendedRegisterForm(RegisterForm):
    recaptcha = RecaptchaField()


class ExtendedForgotPasswordForm(ForgotPasswordForm):
    recaptcha = RecaptchaField()


class ExtendedResetPasswordForm(ResetPasswordForm):
    recaptcha = RecaptchaField()

from django.utils.functional import cached_property

class AccountMixin():

    @cached_property
    def account(self):
        if not self.request.user.is_authenticated:
            return None
        elif hasattr(self.request.user, 'account'):
            return self.request.user.account
        else:
            return None


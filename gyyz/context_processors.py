def device(request):
    '''Add client device type into template contexts.'''
    agent = request.META['HTTP_USER_AGENT'].lower()
    mobile = ['iphone','android','symbianos','windows phone']

    context = dict()
    if any([agent.find(name) + 1 for name in mobile]):
        context['device_type'] = 'mobile'
    else:
        context['device_type'] = 'pc'

    if agent.find('android') + 1:
        context['is_android'] = True

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'com.morch.yisu':
        context['is_app'] = True
    else:
        context['is_app'] = False

    return context


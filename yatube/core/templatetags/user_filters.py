from django import template

register = template.Library()

@register.filter # добавление своего класса css в шаблонах
def addclass(field, css):
    return field.as_widget(attrs={'class': css})

@register.filter # фильтр для шАбЛоНоВ - в таком стиле
def uglify(text):
    modify_text = ''
    x = 0
    for i in text:
        x += 1
        if x % 2 == 0:
            modify_text += i.upper()
        else:
            modify_text += i.lower()
    return modify_text
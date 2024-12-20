from django import forms

class ChineseTextForm(forms.Form):
    chinese_text = forms.CharField(widget=forms.Textarea, initial="感谢您使用我的网站，祝您阅读愉快")

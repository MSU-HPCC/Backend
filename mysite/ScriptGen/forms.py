from django import forms

class NameForm(forms.Form):
    Wall_time = forms.CharField(label='Wall time', max_length=100)
    job_name = forms.CharField(label='Job name', max_length=100)
    script_path = forms.CharField(label='Script Path', max_length=100)

    nodes = forms.IntegerField(label='Nodes', min_value=0)
    memory = forms.CharField(label='Memory', max_length=100)
    CPUs = forms.IntegerField(label='CPUs', min_value=0)
    MemoryPerCPU =forms.CharField(label='Memory/CPU', max_length=100)


from django import forms

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)


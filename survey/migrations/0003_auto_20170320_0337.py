# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_survey_template'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='question_type',
            new_name='type',
        ),
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='answerbase',
            name='question',
            field=models.ForeignKey(related_name='answers', to='survey.Question'),
        ),
        migrations.AlterField(
            model_name='answerbase',
            name='response',
            field=models.ForeignKey(related_name='answers', to='survey.Response'),
        ),
        migrations.AlterField(
            model_name='question',
            name='category',
            field=models.ForeignKey(related_name='related_questions', blank=True, to='survey.Category', null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='choices',
            field=models.TextField(help_text="The choices field is only used if the question type\nif the question type is 'radio', 'select', or\n'select multiple' provide a comma-separated list of\noptions for this question .", null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(related_name='related_questions', to='survey.Survey'),
        ),
    ]

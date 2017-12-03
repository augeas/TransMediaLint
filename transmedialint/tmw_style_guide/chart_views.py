
from django.http import HttpResponse, Http404
from django.db.models import Count
from django.db.models.functions import Trunc
from django.shortcuts import render_to_response

from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import pandas as pd

from .models import RatedArticle
from sources.models import Article, Author, Source

article_models = {'source':Source, 'author':Author}

def groupby_month(q):
    return q.annotate(
        month=Trunc('date_published','month')).order_by('month').values('month').annotate(
            count=Count('month')).values('count','month')
    
def rated_article_chart(request):
    
    filters = {}
    for name, model in article_models.items():
        slug = request.GET.get(name)
        if slug:
            try:
                obj = model.objects.get(slug=slug)
                filters[name] = obj
            except model.DoesNotExist:
                raise Http404('{} {} does not exist.'.format(name.capitalize(), slug))
    
    source = filters.get('source',False)
    if not source:
        raise Http404('No source specified')
    
    articles = Article.objects.filter(**filters)
    
    queries = {'green':groupby_month(articles.filter(ratedarticle=None)),
        'yellow':groupby_month(articles.filter(ratedarticle__rating='yellow')),
        'red':groupby_month(articles.filter(ratedarticle__rating='red'))}
    
    get_df = lambda k,v: pd.DataFrame({k:[q['count'] for q in v]}, index =[q['month'] for q in v])
    
    data = pd.concat([get_df(k,v) for k,v in queries.items()], axis=1).fillna(0.0)
    
    chart_data = ColumnDataSource(data=data)

    x_index = pd.to_datetime(data.index).tolist()
    
    title = 'Articles from {} rated by the TransMediaWatch style-guide'.format(source.title)
    
    fig = figure(plot_width=768, plot_height=512, x_axis_type="datetime", title=title,)
    
    fig.vbar_stack(['green','yellow','red'], x='index', width=0.9, 
        color=["#00ff00", "#ffff00", "#ff0000"],
        source=chart_data,
        legend=['no issues', 'potentially inappropriate medical/legal terms',
            'offensive, inappropriate or inaccurate terms'])
    
    fig.title.text_font_size = "12pt"
    fig.y_range.start = 0
    fig.x_range.range_padding = 0.1
    fig.xgrid.grid_line_color = None
    fig.axis.minor_tick_line_color = None
    fig.xaxis.axis_label = 'date published'
    fig.xaxis.axis_label_text_font_size = '20pt'
    fig.xaxis.major_label_text_font_size = '12pt'
    fig.yaxis.axis_label = 'Number of articles'
    fig.yaxis.axis_label_text_font_size = '20pt'
    fig.yaxis.major_label_text_font_size = '12pt'
    fig.outline_line_color = None
    fig.legend.location = 'top_left'
    fig.legend.orientation = 'vertical'
    
    script, div = components(fig)

    return render_to_response('charts/rated_articles.html',
        {'script':script, 'div': div, 'title':title})
        
    
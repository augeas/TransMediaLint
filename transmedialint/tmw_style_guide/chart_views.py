
from django.http import HttpResponse, Http404
from django.db.models import Count
from django.db.models.functions import ExtractMonth, Trunc
from django.shortcuts import render

from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import pandas as pd

from sources.models import Article, Author, Source
from tmw_style_guide.models import RatedArticle


article_models = {'source':Source, 'author':Author}


def groupby_month(q):
    return q.annotate(
        month=Trunc('date_published','month')).order_by('month').values(
        'month').annotate(count=Count('month')).values('count','month')


def aggregate_month(q):
    return q.annotate(month=ExtractMonth('date_published','month')).values(
        'month').order_by('month').annotate(count=(Count('month')))


def get_rated_df(rating, query):
    counts = [q['count'] for q in query]
    index = [q['month'] for q in query]
    df = pd.DataFrame({rating: counts}, index=index)

    try:    
        df.index = df.index.tz_localize(None)
    except:
        pass
    
    return df


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
    
    year = request.GET.get('year', False)
    if year:
        filters['date_published__year'] = int(year)
                
    source = filters.get('source',False)
    if not source:
        raise Http404('No source specified')
    
    articles = Article.objects.filter(**filters)
    
    queries = {'green':groupby_month(articles.filter(ratedarticle__rating='green')),
        'yellow':groupby_month(articles.filter(ratedarticle__rating='yellow')),
        'red':groupby_month(articles.filter(ratedarticle__rating='red'))}
        
    data = pd.concat(
        filter(lambda df: not df.empty,
            (get_rated_df(k,v) for k,v in queries.items())),
            axis=1).fillna(0.0)
    
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
    fig.xaxis.axis_label = 'month published'
    fig.xaxis.axis_label_text_font_size = '20pt'
    fig.xaxis.major_label_text_font_size = '12pt'
    fig.yaxis.axis_label = 'Number of articles'
    fig.yaxis.axis_label_text_font_size = '20pt'
    fig.yaxis.major_label_text_font_size = '12pt'
    fig.outline_line_color = None
    fig.legend.location = 'top_left'
    fig.legend.orientation = 'vertical'
    
    script, div = components(fig)

    return render(request, 'charts/rated_articles.html',
        {'script':script, 'div': div, 'title':title})
        
    

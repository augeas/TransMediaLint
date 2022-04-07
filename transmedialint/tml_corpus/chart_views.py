
from bokeh import palettes
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
from bokeh.plotting import figure
from django.http import HttpResponse, Http404
from django.db.models import Count
from django.db.models.functions import Trunc
from django.shortcuts import render
import pandas as pd

from sources.models import Source
from tml_corpus.models import ArticleEntity


def entity_stack(source, page, df, ranks, width=1024, height=512,
    page_size=20):
    
    start = page * page_size
    end = page_size * (page + 1)
    
    title = 'Named Entities from {}, rank {} to {}'.format(
        source.name, start + 1, end)
    
    fig = figure(plot_width=width, plot_height=height, x_axis_type="datetime",       
        title=title)
    
    entities = ranks[start:end]
    colour = palettes.d3['Category20'][max(len(entities), 20)]
    
    entities_by_month = df.merge(entities, on='entity__text')[
        ['entity__text', 'month', 'entity__text__count']].pivot(
        'month', 'entity__text', 'entity__text__count').reset_index().set_index(
        'month').asfreq('MS').fillna(0)
        
    chart_data = ColumnDataSource(entities_by_month.reset_index())
    
    entity_labels = list(entities.entity__text)
    
    fig.varea_stack(stackers=entity_labels, x='month',
        legend_label=entity_labels, color=colour, source=chart_data)

    fig.add_layout(fig.legend[0], 'right')

    fig.title.text_font_size = "12pt"
    fig.y_range.start = 0
    fig.x_range.range_padding = 0.1
    fig.xgrid.grid_line_color = None
    fig.axis.minor_tick_line_color = None
    fig.xaxis.axis_label = 'month'
    fig.xaxis.axis_label_text_font_size = '20pt'
    fig.xaxis.major_label_text_font_size = '12pt'
    fig.yaxis.axis_label = 'Number of Occurances'
    fig.yaxis.axis_label_text_font_size = '20pt'
    fig.yaxis.major_label_text_font_size = '12pt'
    fig.outline_line_color = None

    return fig


def source_entity_chart(request):
    slug = request.GET.get('source')
    if not slug:
        raise Http404('No source specified')
    
    try:
        src = Source.objects.get(slug=slug)
    except:
        raise Http404('No such source: {}'.format(slug))
    
    query = ArticleEntity.objects.filter(article__source=src).values(
        'article__date_published', 'entity__text').annotate(
        month=Trunc('article__date_published', 'month')).values(
        'month', 'entity__text').annotate(Count('entity__text')).order_by(
        'month', 'entity__text__count')
        
    df = pd.DataFrame(query.iterator())
    
    top_entities = df.groupby('entity__text').agg(
        {'entity__text__count': 'sum'}).reset_index().sort_values(
        'entity__text__count', ascending=False).rename(
        columns={'entity__text__count': 'total_count'})
        
    pages = len(top_entities[top_entities.total_count>=10]) // 20
    
    charts = [entity_stack(src, page, df, top_entities)
        for page in range(pages)]
    
    script, div = components(column(*charts))
    
    title = 'Named Entities from Articles in {}'.format(src.name)
    
    return render(request, 'charts/chart.html',
        {'script':script, 'div': div, 'title':title})
    



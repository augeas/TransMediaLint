
# Licensed under the Apache License Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.txt
import json

from django.http import HttpResponse, Http404
from django.db.models import Count
from django.db.models.functions import ExtractMonth, Trunc
from django.shortcuts import render

from bokeh.embed import components
from bokeh.models import AnnularWedge, ColumnDataSource, Legend, LegendItem, Plot, Range1d
from bokeh import palettes
from bokeh.plotting import figure
import numpy as np
import pandas as pd

from sources.models import Article, Author, Source
from tmw_style_guide.models import Annotation, RatedArticle


article_models = {'source': Source, 'author': Author}

gyr = {'green': '#00ff00', 'yellow': '#ffff00', 'red': '#ff0000'}

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


def article_filters(request):
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
                
    source = filters.get('source', False)
    if not source:
        raise Http404('No source specified')
    
    return filters


def rated_article_chart(request):
    filters = article_filters(request)
    source = filters['source']
    articles = Article.objects.filter(**filters)
    
    queries = {'green':groupby_month(articles.filter(ratedarticle__rating='green')),
        'yellow':groupby_month(articles.filter(ratedarticle__rating='yellow')),
        'red':groupby_month(articles.filter(ratedarticle__rating='red'))}
        
    data = pd.concat(
        filter(lambda df: not df.empty,
            (get_rated_df(k,v) for k,v in queries.items())),
            axis=1).fillna(0.0)
    
    chart_data = ColumnDataSource(data=data)
    
    title = 'Articles from {} rated by the TransMediaWatch style-guide'.format(source.name)
    
    fig = figure(width=768, height=512, x_axis_type="datetime", title=title,)
    
    fig.vbar_stack(['green','yellow','red'], x='index', width=0.9, 
        color=["#00ff00", "#ffff00", "#ff0000"],
        source=chart_data,
        legend_label=['no issues', 'potentially inappropriate medical/legal terms',
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

    return render(request, 'charts/chart.html',
        {'script':script, 'div': div, 'title':title})


def cumulative_angle(df, source, start, end):
    df[end] = (df[source] * 2 * np.pi).cumsum()
    df[start] = 0
    start_loc = df.columns.get_loc(start)
    end_loc = df.columns.get_loc(end)
    df.iloc[1:, start_loc] = df.iloc[0:-1, end_loc]
    
    
def cat_palette(size):
    if size <= 10:
        return palettes.d3['Category20b'][10][0:size]
    if size <= 20:
        return palettes.d3['Category20b'][size]
    elif size <= 40:
        hsize = size // 2
        return (palettes.d3['Category20b'][hsize]
            + palettes.d3['Category20c'][hsize+1])[0:size]
    else:
        return (palettes.d3['Category20b'][20]
            + palettes.d3['Category20c'][20]
            + palettes.brewer['BrBG'][11])[0:size]

        
def fill_legend(legend, items, render, offset=0):
    for i, item in enumerate(items):
        legend.items.append(LegendItem(
            label=item, renderers=[render], index=offset+i))


def rated_author_chart(request):
    filters = article_filters(request)
    source = filters['source']
    articles = Article.objects.filter(**filters)
    
    query_df = pd.DataFrame(articles.values(
        'author__name', 'ratedarticle__rating').annotate(
        rating_count=Count('ratedarticle__rating')))
        
    author_df = query_df.pivot(
        columns='ratedarticle__rating', index='author__name',
        values='rating_count').fillna(0).reset_index()
    
    if 'red' in author_df.columns:
        author_df.sort_values('red', ascending=False, inplace=True)
    elif 'yellow' in author_df.columns:
        author_df.sort_values('yellow', ascending=False, inplace=True)
    else:
        author_df.sort_values('green', ascending=False, inplace=True)

    present_ratings = [rating for rating in ['red', 'yellow', 'green']
        if rating in author_df.columns]
    author_df['total'] = author_df[present_ratings].sum(axis=1)
    
    total_articles = author_df.total.sum()
    author_df['article_frac'] = author_df.total / total_articles

    if 'red' in author_df.columns:
        total_red_articles = author_df.red.sum()
        red_col = 'red'
    elif 'yellow' in author_df.columns:
         total_red_articles = author_df.yellow.sum()
         red_col = 'yellow'
    else:
        total_red_articles = author_df.green.sum()
        red_col = 'green'
    
    author_df['total_red_frac'] = author_df[red_col] / total_red_articles
    author_df['significant'] = (author_df.total_red_frac.cumsum()
        * 100).diff().fillna(100) >= 1
    
    author_df.reset_index(drop=True, inplace=True)
    
    if len(author_df[author_df.significant]) > 20:
        author_df.loc[0:20, 'significant'] = True
        author_df.loc[20:, 'significant'] = False

    the_others = author_df[~author_df.significant].drop(
        ['author__name', 'significant'], axis=1).sum().to_dict()
    the_others['author__name'] = 'Others ({})'.format(
        len(author_df[~author_df.significant]))
    
    all_author_cols = ('author__name', 'green', 'yellow', 'red',
        'total', 'article_frac', 'total_red_frac')
    author_cols = [col for col in all_author_cols if col in author_df]
    other_cols = [col for col in all_author_cols if col in the_others.keys()]
    rated_authors_df = pd.concat((author_df[author_df.significant][author_cols],
        pd.DataFrame((the_others,))[other_cols]), axis=0)
    
    cumulative_angle(rated_authors_df, 'article_frac', 'total_start_angle',
        'total_end_angle')
    
    top_authors_df = query_df.merge(author_df[author_df.significant][
        ['author__name', 'total_red_frac']], on='author__name')
    
    other_authors_df = query_df.merge(author_df[~author_df.significant][
        ['author__name', 'total_red_frac']], on='author__name')
    
    other_authors = other_authors_df[
        ['ratedarticle__rating', 'rating_count']].groupby(
        'ratedarticle__rating').agg('sum').reset_index().to_dict('records')
    
    for author in other_authors:
        author['author__name'] = 'Others'
        author['total_red_frac'] = -1

    author_fractions_df = pd.concat(
        [top_authors_df, pd.DataFrame(other_authors)], axis=0)
    
    rating_map = {'green': 0, 'yellow': 1, 'red': 2}
    
    author_fractions_df['rating'] = author_fractions_df.ratedarticle__rating.map(
        rating_map.get)
    
    author_fractions_df.sort_values(['total_red_frac', 'rating'],
        ascending=False, inplace=True)

    author_fractions_df['frac'] = author_fractions_df.rating_count / total_articles
    
    cumulative_angle(author_fractions_df, 'frac', 'start_angle', 'end_angle')
    
    author_fractions_df['colours'] = (
        author_fractions_df.ratedarticle__rating.map(gyr))
    
    author_fraction_data = ColumnDataSource(author_fractions_df[
        ['start_angle', 'end_angle', 'colours']].rename(columns={
        'start_angle': 'start', 'end_angle': 'end'}))
        
    inner_ring = AnnularWedge(x=0, y=0, inner_radius=1.25, outer_radius=1.45,
        start_angle="start", end_angle="end", line_width=0, fill_color="colours")
    
    rated_authors_df['colours'] = cat_palette(len(rated_authors_df))
    
    author_total_data = ColumnDataSource(rated_authors_df.rename(
        columns={'total_start_angle': 'start', 'total_end_angle': 'end'})[
        ['start', 'end', 'colours']])
        
    outer_ring = AnnularWedge(x=0, y=0, inner_radius=1.5, outer_radius=2.5,
        start_angle="start", end_angle="end", line_width=0, fill_color="colours")
    
    plot = Plot(x_range=Range1d(start=-3, end=3),
        y_range=Range1d(start=-2, end=2),
        frame_width=400, frame_height=400)
    
    inner_render = plot.add_glyph(author_fraction_data, inner_ring)
    outer_render = plot.add_glyph(author_total_data, outer_ring)
    
    all_authors = list(rated_authors_df.author__name)
    h_authors = len(all_authors) // 2
    
    author_legend1 = Legend(location="left")
    fill_legend(author_legend1, all_authors[0:h_authors], outer_render)
    author_legend2 = Legend(location="left")
    fill_legend(author_legend2, all_authors[h_authors:], outer_render, h_authors)
            
    plot.add_layout(author_legend1, "left")
    plot.add_layout(author_legend2, "right")
    
    rating_legend = Legend(location="left")
    
    fake_df = pd.DataFrame()
    fake_df['label'] = ['no issues', 'potentially inappropriate medical/legal terms',
        'offensive, inappropriate or inaccurate terms']
    fake_df['colours'] = list(gyr.values())
    fake_df['start'] = 0
    fake_df['end'] = 0
    fake_ring = AnnularWedge(x=0, y=0, inner_radius=0, outer_radius=0,
        start_angle="start", end_angle="end", line_width=0,
        fill_color="colours")
    fake_data = ColumnDataSource(fake_df)
    fake_render = plot.add_glyph(fake_data, fake_ring)
    
    fill_legend(rating_legend, fake_df.label, fake_render)
        
    plot.add_layout(rating_legend, 'below')

    script, div = components(plot)
        
    title = 'Articles from {} rated by author'.format(source.name)

    #return HttpResponse('\n'.join(rated_authors_df.author__name))

    
    #return HttpResponse(json.dumps(author_fractions_df[
    #    ['start_angle', 'end_angle', 'colours']].rename(columns={
    #    'start_angle': 'start', 'end_angle': 'end'}).to_dict('records')))

    return render(request, 'charts/chart.html',
        {'script':script, 'div': div, 'title': title})


def annotation_label_chart(request):
    slug = request.GET.get('source')
    if not slug:
        raise Http404('No source specified')
    
    try:
        src = Source.objects.get(slug=slug)
    except:
        raise Http404('No such source: {}'.format(slug))

    if request.GET.get('nouns') == 'true':
        exclude = {}
    else:
        exclude = {'label': 'transgender as a noun'}
    
    query = Annotation.objects.filter(article__source__slug=slug).exclude(
        **exclude).annotate(
        month=Trunc('article__date_published','month')).values(
        'month', 'label').annotate(count=Count('id')).order_by('month')
        
    df = pd.DataFrame(query.iterator())
        
    label_counts_by_month = df.pivot(columns='label', index='month',
        values='count').fillna(0)

    sorted_lables = list(df.groupby('label').agg(
        {'count': 'sum'}).reset_index().sort_values(
        'count', ascending=False).label)[0:20]
    
    colour = palettes.d3['Category20'][len(sorted_lables)]
    
    title = 'Article Annotations from {}'.format(src.name)
    
    chart_data = ColumnDataSource(data=label_counts_by_month)
    
    fig = figure(width=1024, height=512, x_axis_type="datetime",       
        title=title)
    
    fig.varea_stack(stackers=sorted_lables, x='month', legend_label=sorted_lables,
        color=colour, source=chart_data)

    fig.add_layout(fig.legend[0], 'right')

    fig.title.text_font_size = "12pt"
    fig.y_range.start = 0
    fig.x_range.range_padding = 0.1
    fig.xgrid.grid_line_color = None
    fig.axis.minor_tick_line_color = None
    fig.xaxis.axis_label = 'month published'
    fig.xaxis.axis_label_text_font_size = '20pt'
    fig.xaxis.major_label_text_font_size = '12pt'
    fig.yaxis.axis_label = 'Number of annotations'
    fig.yaxis.axis_label_text_font_size = '20pt'
    fig.yaxis.major_label_text_font_size = '12pt'
    fig.outline_line_color = None

    script, div = components(fig)

    return render(request, 'charts/chart.html',
        {'script':script, 'div': div, 'title':title})


def index():
    return locals()

def show():
    #edit=db.edits(request.args(0,cast=int))
    rows=db(db.edits).select(orderby=~db.edits.id,limitby=(0, 50) )
    return locals()
def detail_view():
    detail=db.edits(request.args(0,cast=int))
    return locals()
def most_common(lst):
    return max(set(lst), key=lst.count)
def trendinglang():
    #trendinglang=db(db.edits).select()
    trending=db.executesql("SELECT lang FROM edits")
    trendinglang=most_common(trending)
    counts=trending.count(trendinglang)
    print counts
    return locals()
def history():
    rows=db(db.edits).select(orderby=~db.edits.id,limitby=(0, 150) )
    return locals()
def news():
    rows=db(db.news).select(orderby=~db.news.id,limitby=(0, 10) )
    print rows
    return locals()

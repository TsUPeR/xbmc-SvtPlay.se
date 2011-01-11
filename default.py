import xbmc, xbmcgui, xbmcplugin, xbmcaddon, urllib2, urllib, re, sys, os, time

#Plugin constants
__plugin__ = "SvtPlay.se"
__settings__ = xbmcaddon.Addon(id='plugin.video.svtplay.se')
__language__ = __settings__.getLocalizedString
# __language__(30204)              # this will return localized string from resources/language/<name_of_language>/strings.xml

baseurl = 'http://svtplay.se'
if ( not __settings__.getSetting( "latestSearch" ) ):
        __settings__.setSetting( "latestSearch", '' )

def getData(url):
    request = urllib2.Request(url)
    request.add_header = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
    response = urllib2.urlopen(request)
    data = response.read()
    response.close();

    return data

def getParams():
    param=[]
    params=sys.argv[2]
    if len(params)>=2:
        params=params[0:len(params)-2]
        pairs=params.replace('?','').split('&')
        param = {}
        for i in range(len(pairs)):
            split=pairs[i].split('=')
            if (len(split))==2:
                param[split[0]]=split[1]

    return param

def getStartItems():
    addListItem( "Program A-\xd6" , baseurl + '/alfabetisk', "list-ao")
    addListItem( "Kategorier" , baseurl + "/kategorier", "categories")
    getStartOffering(baseurl)
    #TODO: Rapport and Bolibompa
    addListItem('S\xf6k...', baseurl + "/sok?", "search")
    return

def getProgramsAO(url):
    data = getData(url)
    programs = re.compile('<li>\W+<a href="([^"]+)">([^<]+)</a>\W+</li>').findall(data, re.DOTALL)
    
    for purl, title in programs:
        addListItem(decodeHtmlEntities(title), baseurl+purl, "parts")

    return
    
def getCategories(url):
    data = getData(url)
    ul = re.compile('<ul class="list category-list[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)[0]
    categories = re.compile('<li class="[^"]*">\W+<div class="container">\W*<a href="([^"]+)"[^>]*>\W*<img[^>]+src="([^"]+)[^>]+>\W*<span class="bottom"></span>\W*<span class="[^"]*">([^>]+)</span>').findall(ul, re.DOTALL)

    for curl, image, title in categories:
        if (curl[0] != "/"):
            curl = "/"+curl

        addListItem(decodeHtmlEntities(title), baseurl + curl, "categoryprograms", image)

def getStartOffering(url):
    data = getData(url)
    ul = re.compile('<ul class="navigation playerbrowser">[\W\w]+?</ul>').findall(data, re.DOTALL)[0]
    parts = re.compile('<li class="[^"]*">\W+(<h2>)*\W*<a href="([^"]+)"[^>]+>([^<]+)</a>').findall(ul, re.DOTALL)
    if len(parts) == 1:
        getEpisodes(url+urllib.unquote_plus(parts[0][1]))
    else:
        for h2, purl, title in parts:
            if title[0:4] == "Live":
                if (purl[0] != "/"):
                        purl = "/" + purl
                addListItem(decodeHtmlEntities(title), url + purl, "episodes")
            else:         
                if purl[0:17] == "http://svtplay.se":
                    addListItem(decodeHtmlEntities(title), purl, "categoryprograms")
                else:
                    if (purl[0] != "/"):
                        purl = "/" + purl
                    addListItem(decodeHtmlEntities(title), url + purl, "categoryprograms")
    return
    
def getCategoryPrograms(url):
    data = getData(url)
    uls = re.compile('<ul class="list[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)
    pages = re.compile('<ul class="list {pagenum:(\d+)[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)
    if pages:
        pagecount = int(pages[0])
    else:
        pagecount = 0
        
    for ul in uls:
        programs = re.compile('<li class="[^"]*">\W*<a href="([^"]+)"[^>]*>\W*<img[^>]+src="([^"]+)[^>]+>\W*(<!--[^/]+/span -->\W+){0,1}<span {0,1}>([^>]+)</span>').findall(ul, re.DOTALL)
        for purl, image, co, title in programs:
            if purl[0:17] == "http://svtplay.se":
                addListItem(decodeHtmlEntities(title.strip()), purl, "parts", image)
            else:
                if (purl[0] != "/"):
                    purl = "/"+purl
                addListItem(decodeHtmlEntities(title.strip()), baseurl + purl, "parts", image)
        
    it = url[url.rindex('/') + 1:len(url)].split(',')
    
    
    if len(it) == 1:
        it = ["pb", "a1364150", "1", "f", "-1"]
    #TODO: Add support for pagination, or?
    current = int(it[2])
    if (current < pagecount):
        it[2] = str(current + 1)
        addListItem("N\xe4sta sida...", "http://svtplay.se/c/96251/barn?ajax,pb/" + ','.join(it), "categoryprograms")

def getProgramParts(url):
    data = getData(url)
    ul = re.compile('<ul class="navigation playerbrowser">[\W\w]+?</ul>').findall(data, re.DOTALL)[0]
    parts = re.compile('<li class="[^"]*">\W+(<h2>)*\W*<a href="([^"]+)"[^>]+>([^<]+)</a>').findall(ul, re.DOTALL)
    if len(parts) == 1:
        getEpisodes(url+urllib.unquote_plus(parts[0][1]))
    else:
        for h2, purl, title in parts:
            if purl[0:17] == "http://svtplay.se":
                addListItem(decodeHtmlEntities(title), purl, "episodes")
            else:
                if (purl[0] != "/"):
                    purl = "/" + purl
                addListItem(decodeHtmlEntities(title), url + purl, "episodes")
    return

def getEpisodes(url):
    data = getData(url)
    #Support for Live
    # <div class="list {pagenum:1} tableau">
    live = re.compile('<div class="list {pagenum:1} tableau">').findall(data, re.DOTALL)
    #support for search
    hit = re.compile('<ul class="list small[^"]*pagenum:(\d+)[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)
    if live:
        ul = re.compile('<ul class="first-child constanthighlight">[\W\w]+?</ul>').findall(data, re.DOTALL)
        if ul:
            ul = ul[0]
            liveShow = re.compile('<h3 class="expandcollapse">([\W\w]+?)</h3>[\W\w]+?href="([^"]+)">[\W\w]+?" src="([^"]+)"[\W\w]+?description">[^>]+([\W\w]+?)</a').findall(ul, re.DOTALL)
            for title, lurl, image, info in liveShow:
                title = title.replace("&nbsp;", " ")
                title = title.replace("\n", "")
                title = title.expandtabs(0)
                addListItem(title.lstrip(), baseurl + lurl, "play", image, False)
    elif hit:
        pagecount = int(hit[0])
        ul = re.compile('<ul class="list small[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)[0]
        
        episodes = re.compile('<li class="[^"]*"\W*>\W+<a href="([^"]+)"[^>]+title="([^"]*)"[^>]+>\W+<img[^>]+src="([^"]+)[^>]+>\W+(<!--[^/]+/span -->\W+){0,1}<span[^>]*>([^<]+)</span>').findall(ul, re.DOTALL)
        for purl, info, image, comment, title in episodes:
            if purl[0:7] != "http://":
                addListItem(title.strip(), baseurl + purl, "play", image, False)
        
        it = url[url.rindex('/') + 1:len(url)].split(',')
        current = int(it[2])
        #TODO: Add support for pagination, or?
        if (current < pagecount):
            it[2] = str(current + 1)
            addListItem( "N\xe4sta sida...", url[0:url.rindex('/') + 1] + ','.join(it), "episodes")
    else:
        xbmcgui.Dialog().ok("Fel", "Hittade inget")
        getStartItems()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return

def getSearch(url):
    searchString = unikeyboard(__settings__.getSetting( "latestSearch" ), __language__( 30202 ) )
    if searchString == "":
        xbmcgui.Dialog().ok( __language__( 30204 ), __language__( 30205 ) )
    elif searchString:
        latestSearch = __settings__.setSetting( "latestSearch", searchString )
        dialogProgress = xbmcgui.DialogProgress()
        dialogProgress.create("SvtPlay.se", __language__( 30207 ) , searchString)
        #The XBMC onscreen keyboard outputs utf-8 and this need to be encoded to unicode
        encodedSearchString = urllib.quote_plus(searchString.decode("utf_8").encode("raw_unicode_escape"))
        #http://svtplay.se/sok?cs,s,1,design,sample/ps,s,1,design,full/ts,s,1,design,title
        url = url + "cs,s,1," + encodedSearchString + ",sample/ps,s,1," + encodedSearchString + ",full/ts,s,1," + encodedSearchString + ",title"
        getEpisodes(url)
    return

def getDownload(url):
    path = __settings__.getSetting( "downloadPath" )
    if (not path):
        xbmcgui.Dialog().ok( __language__( 30204 ), __language__( 30208 ))
        __settings__.openSettings()
        path = __settings__.getSetting( "downloadPath" )
    
    dQuality = int(__settings__.getSetting( "downloadQuality" ))
    params=getParams()
    lurl=None
    name=None
    try:
        lurl=urllib.unquote_plus(params["url"])
    except:
        pass
        
    
    try:
        name=urllib.unquote_plus(params["name"])
    except:
        pass
        
    videolink = getPlayUrl(lurl, dQuality)
    
    if not videolink[dQuality]:
        if not videolink[4]:
            #Show Alert dialog
            xbmcgui.Dialog().ok("Fel", "Hittade ingen videol\xe4nk ")
        else:
            if ".mp4" in videolink[4][0]:
                vurl = videolink[4][0]
            else:
                xbmcgui.Dialog().ok("Fel", "Hittade ingen videol\xe4nk ")
    else:
        vurl = videolink[dQuality][0]
    
    #Debug
    if vurl:
        command = ("rtmpdump -r \"%s\" -o \"%s%s.mp4\"") % (vurl, path, name.replace(" ","."))
        print "DEBUG __plugin__ rtmpdump:" + command
        xbmc.executebuiltin("System.Exec(" + command + ")")

#From old undertexter.se plugin    
def unikeyboard(default, message):
    keyboard = xbmc.Keyboard(default, message)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return keyboard.getText()
    else:
        return None
    
def play(url,name):
    quality = int(__settings__.getSetting( "quality" ))
    videolink = getPlayUrl(url, quality)
    item=xbmcgui.ListItem(name, iconImage='', thumbnailImage='')
    item.setInfo(type="Video", infoLabels={ "Title": name})
    if not videolink[quality]:
        if not videolink[4]:
            print "No videolink !!!"
            #Show Alert dialog
            xbmcgui.Dialog().ok( __language__( 30204 ), __language__( 30208 ))
        else:
            #Check if live stream (no .mp4 extension)
            if not ".mp4" in videolink[4][0]:
                item.setProperty("IsLive", "true")
            xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(videolink[4][0], item)
    else:
        print "VideolinkHD " + videolink[quality][0]
        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(videolink[quality][0], item)

def getPlayUrl(url, quality):
    #DEBUG videolink="rtmpe://fl11.c90909.cdn.qbrick.com/90909/_definst_/kluster/20110101/PG-1122415-006A-PLANETSKETCHS-01-mp4-d-v1.mp4"
    #videolinkExt = "rtmp://fl10.c00928.cdn.qbrick.com/00928/enc2low_h264/flowcontrol"
    #value="dynamicStreams=url:rtmpe://fl11.c90909.cdn.qbrick.com/90909/_definst_/kluster/20110104/PG-1128051-012A-SHAUNTHESHEEP2-02-C0-mp4-e-v1.mp4,bitrate:2400
    #|url:rtmpe://fl11.c90909.cdn.qbrick.com/90909/_definst_/kluster/20110104/PG-1128051-012A-SHAUNTHESHEEP2-02-C0-mp4-d-v1.mp4,bitrate:1400
    #|url:rtmpe://fl11.c90909.cdn.qbrick.com/90909/_definst_/kluster/20110104/PG-1128051-012A-SHAUNTHESHEEP2-02-C0-mp4-c-v1.mp4,bitrate:850
    #|url:rtmpe://fl11.c90909.cdn.qbrick.com/90909/_definst_/kluster/20110104/PG-1128051-012A-SHAUNTHESHEEP2-02-C0-mp4-b-v1,bitrate:320&
    data = getData(url)
    videolinkExt = re.compile('<a class="external-player".*href="(.*)"').findall(data, re.DOTALL)
    videolink = []
    videolink.append(re.compile('=url:(rtmp.*),bitrate:2400\|').findall(data, re.DOTALL))
    videolink.append(re.compile('2400\|url:(rtmp.*),bitrate:1400\|').findall(data, re.DOTALL))
    videolink.append(re.compile('1400\|url:(rtmp.*),bitrate:850\|').findall(data, re.DOTALL))
    videolink.append(re.compile('850\|url:(rtmp.*),bitrate:320&').findall(data, re.DOTALL))
    videolink.append(videolinkExt)
    return videolink

def addListItem(name,url,mode,iconimage='',folder=True):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + urllib.quote_plus(mode) + "&name=" + urllib.quote_plus(name)
    li=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    li.setInfo(type="Video", infoLabels={ "Title": name })
    #Download support
    if (mode == "play") and ( __settings__.getSetting( "downloadPath" ) != ""):
        cm = []
        durl = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=download" + "&name=" + urllib.quote_plus(name)
        cm.append(( __language__( 30209 ) , "XBMC.RunPlugin(%s)" % (durl)))
        li.addContextMenuItems( cm, replaceItems=False )
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=li, isFolder=folder)


def decodeHtmlEntities(string):
    return string.replace("&quot;", "\"").replace("&amp;", "&")

params=getParams()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass

try:
        name=urllib.unquote_plus(params["name"])
except:
    pass

try:
        mode=urllib.unquote_plus(params["mode"])
except:
    pass

if mode==None or url==None or len(url)<1:
        getStartItems()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
if mode=="list-ao":
        getProgramsAO(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
if mode=="categories":
        getCategories(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
if mode=="categoryprograms":
        getCategoryPrograms(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode=="parts":
        getProgramParts(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode=="episodes":
        getEpisodes(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode=="play":
        play(url,name)
elif mode=="search":
        getSearch(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode=="download":
        getDownload(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))





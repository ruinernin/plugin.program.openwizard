import xbmc

import glob
import os

from datetime import datetime
from datetime import timedelta

import uservar
from resources.libs import logging
from resources.libs import tools


def flush_old_cache():
    if not os.path.exists(vars.TEXTCACHE):
        os.makedirs(vars.TEXTCACHE)
    try:
        age = int(float(uservar.CACHEAGE))
    except:
        age = 30
    match = glob.glob(os.path.join(vars.TEXTCACHE, '*.txt'))
    for file in match:
        file_modified = datetime.fromtimestamp(os.path.getmtime(file))
        if datetime.now() - file_modified > timedelta(minutes=age):
            logging.log("Found: {0}".format(file))
            os.remove(file)


def text_cache(url):
    try:
        age = int(float(uservar.CACHEAGE))
    except:
        age = 30
    if uservar.CACHETEXT.lower() == 'yes':
        spliturl = url.split('/')
        if not os.path.exists(vars.TEXTCACHE):
            os.makedirs(vars.TEXTCACHE)
        file = xbmc.makeLegalFilename(os.path.join(vars.TEXTCACHE, spliturl[-1]+'_'+spliturl[-2]+'.txt'))
        if os.path.exists(file):
            file_modified = datetime.fromtimestamp(os.path.getmtime(file))
            if datetime.now() - file_modified > timedelta(minutes=age):
                if tools.working_url(url):
                    os.remove(file)

        if not os.path.exists(file):
            if not tools.working_url(url):
                return False
            textfile = tools.open_url(url)
            content = tools.basecode(textfile, True)
            tools.write_to_file(file, content)

        a = tools.basecode(tools.read_from_file(file), False)
        return a
    else:
        textfile = tools.open_url(url)
        return textfile


def clear_packages(over=None):
    if os.path.exists(PACKAGES):
        try:
            for root, dirs, files in os.walk(PACKAGES):
                file_count = 0
                file_count += len(files)
                if file_count > 0:
                    size = convertSize(getSize(PACKAGES))
                    if over:
                        yes = 1
                    else:
                        yes = DIALOG.yesno("[COLOR %s]Delete Package Files" % COLOR2,
                                           "[COLOR %s]%s[/COLOR] files found / [COLOR %s]%s[/COLOR] in size." % (
                                           COLOR1, str(file_count), COLOR1, size),
                                           "Do you want to delete them?[/COLOR]",
                                           nolabel='[B][COLOR red]Don\'t Clear[/COLOR][/B]',
                                           yeslabel='[B][COLOR springgreen]Clear Packages[/COLOR][/B]')
                    if yes:
                        for f in files: os.unlink(os.path.join(root, f))
                        for d in dirs: shutil.rmtree(os.path.join(root, d))
                        LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
                                  '[COLOR %s]Clear Packages: Success![/COLOR]' % COLOR2)
                else:
                    LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
                              '[COLOR %s]Clear Packages: None Found![/COLOR]' % COLOR2)
        except Exception as e:
            LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
                      '[COLOR %s]Clear Packages: Error![/COLOR]' % COLOR2)
            log("Clear Packages Error: %s" % str(e), xbmc.LOGERROR)
    else:
        LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
                  '[COLOR %s]Clear Packages: None Found![/COLOR]' % COLOR2)


def clear_packages_startup():
    start = datetime.utcnow() - timedelta(minutes=3)
    file_count = 0;
    cleanupsize = 0
    if os.path.exists(PACKAGES):
        pack = os.listdir(PACKAGES)
        pack.sort(key=lambda f: os.path.getmtime(os.path.join(PACKAGES, f)))
        try:
            for item in pack:
                file = os.path.join(PACKAGES, item)
                lastedit = datetime.utcfromtimestamp(os.path.getmtime(file))
                if lastedit <= start:
                    if os.path.isfile(file):
                        file_count += 1
                        cleanupsize += os.path.getsize(file)
                        os.unlink(file)
                    elif os.path.isdir(file):
                        cleanupsize += getSize(file)
                        cleanfiles, cleanfold = cleanHouse(file)
                        file_count += cleanfiles + cleanfold
                        try:
                            shutil.rmtree(file)
                        except Exception as e:
                            log("Failed to remove %s: %s" % (file, str(e), xbmc.LOGERROR))
            if file_count > 0:
                LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
                          '[COLOR %s]Clear Packages: Success: %s[/COLOR]' % (COLOR2, convertSize(cleanupsize)))
            else:
                LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
                          '[COLOR %s]Clear Packages: None Found![/COLOR]' % COLOR2)
        except Exception as e:
            LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
                      '[COLOR %s]Clear Packages: Error![/COLOR]' % COLOR2)
            log("Clear Packages Error: %s" % str(e), xbmc.LOGERROR)
    else:
        LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
                  '[COLOR %s]Clear Packages: None Found![/COLOR]' % COLOR2)


def clear_archive():
    if os.path.exists(ARCHIVE_CACHE):
        cleanHouse(ARCHIVE_CACHE)


def clear_function_cache():
    if xbmc.getCondVisibility('System.HasAddon(script.module.resolveurl)'): xbmc.executebuiltin(
        'RunPlugin(plugin://script.module.resolveurl/?mode=reset_cache)')
    if xbmc.getCondVisibility('System.HasAddon(script.module.urlresolver)'): xbmc.executebuiltin(
        'RunPlugin(plugin://script.module.urlresolver/?mode=reset_cache)')


def clear_cache(over=None):
    PROFILEADDONDATA = os.path.join(PROFILE, 'addon_data')
    dbfiles = [
        ## TODO: Double check these
        (os.path.join(ADDOND, 'plugin.video.placenta', 'cache.db')),
        (os.path.join(ADDOND, 'plugin.video.placenta', 'cache.meta.5.db')),
        (os.path.join(ADDOND, 'plugin.video.placenta', 'cache.providers.13.db')),
        (os.path.join(ADDOND, 'plugin.video.gaia', 'cache.db')),
        (os.path.join(ADDOND, 'plugin.video.gaia', 'meta.db')),
        (os.path.join(ADDOND, 'plugin.video.exodusredux', 'cache.db')),
        (os.path.join(ADDOND, 'plugin.video.exodusredux', 'meta.5.db')),
        (os.path.join(ADDOND, 'plugin.video.exodusredux', 'cache.providers.13.db')),
        (os.path.join(ADDOND, 'plugin.video.overeasy', 'cache.db')),
        (os.path.join(ADDOND, 'plugin.video.overeasy', 'meta.5.db')),
        (os.path.join(ADDOND, 'plugin.video.overeasy', 'cache.providers.13.db')),
        (os.path.join(ADDOND, 'plugin.video.yoda', 'cache.db')),
        (os.path.join(ADDOND, 'plugin.video.yoda', 'meta.5.db')),
        (os.path.join(ADDOND, 'plugin.video.yoda', 'cache.providers.13.db')),
        (os.path.join(ADDOND, 'plugin.video.scrubsv2', 'cache.db')),
        (os.path.join(ADDOND, 'plugin.video.scrubsv2', 'meta.5.db')),
        (os.path.join(ADDOND, 'plugin.video.scrubsv2', 'cache.providers.13.db')),
        (os.path.join(ADDOND, 'plugin.video.seren', 'cache.db')),
        (os.path.join(ADDOND, 'plugin.video.seren', 'torrentScrape.db')),
        (os.path.join(ADDOND, 'script.module.simplecache', 'simplecache.db'))]

    cachelist = [
        (PROFILEADDONDATA),
        (ADDOND),
        (os.path.join(HOME, 'cache')),
        (os.path.join(HOME, 'temp')),
        (os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')),
        (os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')),
        (os.path.join(ADDOND, 'script.module.simple.downloader')),
        (os.path.join(ADDOND, 'plugin.video.itv', 'Images')),
        (os.path.join(PROFILEADDONDATA, 'script.module.simple.downloader')),
        (os.path.join(PROFILEADDONDATA, 'plugin.video.itv', 'Images')),
        (os.path.join(ADDOND, 'script.extendedinfo', 'images')),
        (os.path.join(ADDOND, 'script.extendedinfo', 'TheMovieDB')),
        (os.path.join(ADDOND, 'script.extendedinfo', 'YouTube')),
        (os.path.join(ADDOND, 'plugin.program.autocompletion', 'Google')),
        (os.path.join(ADDOND, 'plugin.program.autocompletion', 'Bing')),
        (os.path.join(ADDOND, 'plugin.video.openmeta', '.storage'))]

    delfiles = 0
    excludes = ['meta_cache', 'archive_cache']
    for item in cachelist:
        if not os.path.exists(item): continue
        if not item in [ADDOND, PROFILEADDONDATA]:
            for root, dirs, files in os.walk(item):
                dirs[:] = [d for d in dirs if d not in excludes]
                file_count = 0
                file_count += len(files)
                if file_count > 0:
                    for f in files:
                        if not f in LOGFILES:
                            try:
                                os.unlink(os.path.join(root, f))
                                log("[Wiped] %s" % os.path.join(root, f), xbmc.LOGNOTICE)
                                delfiles += 1
                            except:
                                pass
                        else:
                            log('Ignore Log File: %s' % f, xbmc.LOGNOTICE)
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                            delfiles += 1
                            log("[Success] cleared %s files from %s" % (str(file_count), os.path.join(item, d)),
                                xbmc.LOGNOTICE)
                        except:
                            log("[Failed] to wipe cache in: %s" % os.path.join(item, d), xbmc.LOGNOTICE)
        else:
            for root, dirs, files in os.walk(item):
                dirs[:] = [d for d in dirs if d not in excludes]
                for d in dirs:
                    if not str(d.lower()).find('cache') == -1:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                            delfiles += 1
                            log("[Success] wiped %s " % os.path.join(root, d), xbmc.LOGNOTICE)
                        except:
                            log("[Failed] to wipe cache in: %s" % os.path.join(item, d), xbmc.LOGNOTICE)
    if INCLUDEVIDEO == 'true' and over is None:
        files = []
        if INCLUDEALL == 'true':
            files = dbfiles
        else:
            ## TODO: Double check these
            if INCLUDEPLACENTA == 'true':
                files.append(os.path.join(ADDOND, 'plugin.video.placenta', 'cache.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.placenta', 'meta.5.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.placenta', 'providers.13.db'))
            if INCLUDEEXODUSREDUX == 'true':
                files.append(os.path.join(ADDOND, 'plugin.video.exodusredux', 'cache.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.exodusredux', 'meta.5.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.exodusredux', 'providers.13.db'))
            if INCLUDEYODA == 'true':
                files.append(os.path.join(ADDOND, 'plugin.video.yoda', 'cache.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.yoda', 'meta.5.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.yoda', 'providers.13.db'))
            if INCLUDEVENOM == 'true':
                files.append(os.path.join(ADDOND, 'plugin.video.venom', 'cache.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.venom', 'meta.5.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.venom', 'providers.13.db'))
            if INCLUDESCRUBS == 'true':
                files.append(os.path.join(ADDOND, 'plugin.video.scrubsv2', 'cache.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.scrubsv2', 'meta.5.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.scrubsv2', 'providers.13.db'))
            if INCLUDEOVEREASY == 'true':
                files.append(os.path.join(ADDOND, 'plugin.video.overeasy', 'cache.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.overeasy', 'meta.5.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.overeasy', 'providers.13.db'))
            if INCLUDEGAIA == 'true':
                files.append(os.path.join(ADDOND, 'plugin.video.gaia', 'cache.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.gaia', 'meta.db'))
            if INCLUDESEREN == 'true':
                files.append(os.path.join(ADDOND, 'plugin.video.seren', 'cache.db'))
                files.append(os.path.join(ADDOND, 'plugin.video.seren', 'torrentScrape.db'))
        if len(files) > 0:
            for item in files:
                if os.path.exists(item):
                    delfiles += 1
                    try:
                        textdb = database.connect(item)
                        textexe = textdb.cursor()
                    except Exception as e:
                        log("DB Connection error: %s" % str(e), xbmc.LOGERROR)
                        continue
                    if 'Database' in item:
                        try:
                            textexe.execute("DELETE FROM url_cache")
                            textexe.execute("VACUUM")
                            textdb.commit()
                            textexe.close()
                            log("[Success] wiped %s" % item, xbmc.LOGNOTICE)
                        except Exception as e:
                            log("[Failed] wiped %s: %s" % (item, str(e)), xbmc.LOGNOTICE)
                    else:
                        textexe.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
                        for table in textexe.fetchall():
                            try:
                                textexe.execute("DELETE FROM %s" % table[0])
                                textexe.execute("VACUUM")
                                textdb.commit()
                                log("[Success] wiped %s in %s" % (table[0], item), xbmc.LOGNOTICE)
                            except Exception as e:
                                try:
                                    log("[Failed] wiped %s in %s: %s" % (table[0], item, str(e)), xbmc.LOGNOTICE)
                                except:
                                    pass
                        textexe.close()
        else:
            log("Clear Cache: Clear Video Cache Not Enabled", xbmc.LOGNOTICE)
    LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),
              '[COLOR %s]Clear Cache: Removed %s Files[/COLOR]' % (COLOR2, delfiles))


def purge_db(name):
	#dbfile = name.replace('.db','').translate(None, digits)
	#if dbfile not in ['Addons', 'ADSP', 'Epg', 'MyMusic', 'MyVideos', 'Textures', 'TV', 'ViewModes']: return False
	#textfile = os.path.join(DATABASE, name)
	log('Purging DB %s.' % name, xbmc.LOGNOTICE)
	if os.path.exists(name):
		try:
			textdb = database.connect(name)
			textexe = textdb.cursor()
		except Exception as e:
			log("DB Connection Error: %s" % str(e), xbmc.LOGERROR)
			return False
	else: log('%s not found.' % name, xbmc.LOGERROR); return False
	textexe.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
	for table in textexe.fetchall():
		if table[0] == 'version':
			log('Data from table `%s` skipped.' % table[0], xbmc.LOGDEBUG)
		else:
			try:
				textexe.execute("DELETE FROM %s" % table[0])
				textdb.commit()
				log('Data from table `%s` cleared.' % table[0], xbmc.LOGDEBUG)
			except Exception as e: log("DB Remove Table `%s` Error: %s" % (table[0], str(e)), xbmc.LOGERROR)
	textexe.close()
	log('%s DB Purging Complete.' % name, xbmc.LOGNOTICE)
	show = name.replace('\\', '/').split('/')
	LogNotify("[COLOR %s]Purge Database[/COLOR]" % COLOR1, "[COLOR %s]%s Complete[/COLOR]" % (COLOR2, show[len(show)-1]))

def old_thumbs():
	dbfile = os.path.join(DATABASE, latestDB('Textures'))
	use    = 30
	week   = TODAY - timedelta(days=7)
	ids    = []
	images = []
	size   = 0
	if os.path.exists(dbfile):
		try:
			textdb = database.connect(dbfile)
			textexe = textdb.cursor()
		except Exception as e:
			log("DB Connection Error: %s" % str(e), xbmc.LOGERROR)
			return False
	else: log('%s not found.' % dbfile, xbmc.LOGERROR); return False
	textexe.execute("SELECT idtexture FROM sizes WHERE usecount < ? AND lastusetime < ?", (use, str(week)))
	found = textexe.fetchall()
	for rows in found:
		idfound = rows[0]
		ids.append(idfound)
		textexe.execute("SELECT cachedurl FROM texture WHERE id = ?", (idfound, ))
		found2 = textexe.fetchall()
		for rows2 in found2:
			images.append(rows2[0])
	log("%s total thumbs cleaned up." % str(len(images)), xbmc.LOGNOTICE)
	for id in ids:
		textexe.execute("DELETE FROM sizes   WHERE idtexture = ?", (id, ))
		textexe.execute("DELETE FROM texture WHERE id        = ?", (id, ))
	textexe.execute("VACUUM")
	textdb.commit()
	textexe.close()
	for image in images:
		path = os.path.join(THUMBS, image)
		try:
			imagesize = os.path.getsize(path)
			os.remove(path)
			size += imagesize
		except:
			pass
	removed = convertSize(size)
	if len(images) > 0: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Thumbs: %s Files / %s MB[/COLOR]!' % (COLOR2, str(len(images)), removed))
	else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Thumbs: None Found![/COLOR]' % COLOR2)
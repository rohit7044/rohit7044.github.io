"""Browser integration checks. Run against a locally running Vite server."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

out=Path('test-results');out.mkdir(exist_ok=True)
results=[]
base=os.environ.get('SITE_BASE_URL','http://127.0.0.1:5173')
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chromium',headless=True,args=['--enable-unsafe-swiftshader'])
    for width in (1440,768,390):
        context=browser.new_context(viewport={'width':width,'height':1000},has_touch=width==390)
        page=context.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        page.goto(base+'/',wait_until='networkidle')
        page.locator('canvas').wait_for()
        page.wait_for_function("document.querySelector('canvas')?.dataset.source==='google/GNM'")
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'Overflow at {width}'
        assert page.locator('h1').inner_text().startswith('Giving shape')
        canvas=page.locator('canvas');before=canvas.get_attribute('data-yaw')
        canvas.focus();page.keyboard.press('ArrowRight');page.wait_for_timeout(300)
        assert before!=canvas.get_attribute('data-yaw')
        box=canvas.bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down();page.mouse.move(box['x']+box['width']/2+60,box['y']+box['height']/2+20,steps=5);page.mouse.up();page.wait_for_timeout(300)
        if width==390:
            before_touch=canvas.get_attribute('data-yaw')
            cdp=context.new_cdp_session(page)
            tx=box['x']+box['width']/2;ty=box['y']+box['height']/2
            cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':tx,'y':ty}]})
            cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':tx-40,'y':ty+5}]})
            cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            page.wait_for_timeout(300)
            assert before_touch!=canvas.get_attribute('data-yaw'),'Touch rotation failed'
        assert page.get_by_role('button',name='Topology',exact=True).count()==0
        assert page.get_by_role('button',name='Teeth & gums',exact=True).count()==0
        assert page.locator('.face-study .face-note').count()==0
        assert 'Research & Engineering' in page.locator('footer').inner_text()
        page.get_by_role('button',name='Expression',exact=True).click()
        page.locator('#expression').fill('70')
        assert page.locator('output').inner_text()=='70%'
        assert page.locator('#pose option[value=wide_smile]').count()==0
        page.locator('#pose').select_option('smile')
        assert page.locator('output').inner_text()=='100%'
        assert float(canvas.get_attribute('data-expression-delta'))>0
        page.locator('#expression').fill('0')
        neutral_pixels=canvas.screenshot()
        for name in ('jaw_open','smile','pucker','wink_left'):
            page.locator('#pose').select_option(name)
            assert canvas.get_attribute('data-expression')==name
            assert float(canvas.get_attribute('data-expression-delta'))>0
            assert canvas.screenshot()!=neutral_pixels,f'{name}: no visible deformation'
            if width==1440:
                canvas.screenshot(path=str(out/f'gnm-{name}.png'))
        page.get_by_role('button',name='Reset').click();page.wait_for_timeout(400)
        assert abs(float(canvas.get_attribute('data-yaw'))+.16)<.01
        page.get_by_role('button',name='Surface',exact=True).click()
        if width==390:
            page.get_by_role('button',name='Menu').click();page.locator('nav').get_by_role('link',name='Research',exact=True).click()
            assert page.get_by_role('button',name='Menu').get_attribute('aria-expanded')=='false'
        page.locator('summary').first.click();assert page.locator('details').first.get_attribute('open') is not None
        page.locator('summary').first.click()
        for anchor in page.locator('a[href^="#"]').all():
            target=anchor.get_attribute('href')[1:]
            assert page.locator('[id="'+target+'"]').count(),target
        assert page.request.get(base+'/assets/resume.pdf').headers['content-type'].startswith('application/pdf')
        page.evaluate('scrollTo(0,0)');page.wait_for_timeout(100)
        page.screenshot(path=str(out/f'desktop-{width}.png'),full_page=True)
        page.locator('.hero').screenshot(path=str(out/f'hero-{width}.png'))
        assert not errors,errors
        results.append({'width':width,'errors':errors,'surface_triangles':int(canvas.get_attribute('data-triangles')),'last_cpu_render_submission_ms':float(canvas.get_attribute('data-render-ms')),'keyboard_drag_modes_expression_reset_navigation_resume_overflow':'passed','touch':'passed' if width==390 else 'not applicable'})
        context.close()
    for scenario in ('reduced-motion','no-webgl','asset-failure'):
        context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce' if scenario=='reduced-motion' else 'no-preference')
        if scenario=='no-webgl':context.add_init_script("const original=HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext=function(type,...args){return type.includes('webgl')?null:original.call(this,type,...args)}")
        if scenario=='asset-failure':context.route('**/assets/face-manifest.json',lambda route:route.abort())
        page=context.new_page();page.goto(base+'/',wait_until='networkidle')
        page.locator('img[src="/assets/face-poster.png"]').wait_for(state='visible')
        assert page.get_by_role('button',name='Surface',exact=True).is_disabled()
        results.append({'fallback':scenario,'result':'passed'})
        context.close()
    browser.close()
(out/'browser-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))

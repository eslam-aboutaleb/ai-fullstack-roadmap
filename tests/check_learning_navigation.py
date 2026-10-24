"""Behavior checks for finding and practicing advanced scenarios."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check(page, base):
    page.goto(base + '/design-scenarios.html')
    scenario_count = page.locator('main .map-card li a').count()
    link = page.locator('main a').filter(has_text='100 GB file with a server').first
    link.click()
    page.wait_for_function('window.GuideAppReady === true')
    target = page.locator(page.evaluate('location.hash'))
    assert target.locator('details.answer').get_attribute('open') is not None
    assert target.locator('.answer-diagram').count() == 1
    page.locator('#question-finder > summary').click()
    page.locator('#chapter-question-kind').select_option(label='Advanced scenario')
    page.locator('#chapter-question-query').fill('100 GB')
    assert page.locator('.finder-results li:visible').count() == 1
    # Directory filtering must not remove the actual learning content.
    assert page.locator('#interview .interview-question').count() > 1
    page.locator('#chapter-question-query').fill('no-such-question-xyz')
    assert page.locator('#chapter-question-empty').is_visible()
    page.locator('#chapter-question-reset').click()
    assert page.locator('.finder-results li:visible').count() == page.locator('.finder-results li').count()
    assert page.locator('#chapter-question-query').evaluate('(el) => el === document.activeElement')
    page.locator('#expand').click()
    assert page.locator('#expand').inner_text() == 'Hide all answers'
    page.locator('#expand').click()
    assert page.locator('details.answer[open]').count() == 0
    assert page.locator('#practice').get_attribute('aria-pressed') == 'false'
    page.locator('#chapter-question-query').fill('100 GB')
    page.locator('.finder-results li:visible a').click()
    # Re-clicking the current hash should still reopen an answer after closing it.
    assert target.locator('details.answer').get_attribute('open') is not None
    for width in (390, 1440):
        page.set_viewport_size({'width': width, 'height': 1000})
        page.locator('#question-finder').scroll_into_view_if_needed()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        page.screenshot(path=f'/tmp/roadmap-design-navigation-{width}.png')
    page.set_viewport_size({'width': 1280, 'height': 720})
    page.goto(base + '/design-scenarios.html')
    page.get_by_role('link', name='How do you reject a stale worker result after its job has been reclaimed?', exact=True).click()
    page.wait_for_function('window.GuideAppReady === true')
    answer = page.locator(page.evaluate('location.hash'))
    assert answer.locator('details.answer').get_attribute('open') is not None
    assert 'attempt' in answer.locator('pre code').first.inner_text()
    assert answer.locator('.answer-diagram').count() == 1
    page.goto(base + '/design-scenarios.html')
    page.get_by_role('link', name='How do you bind encrypted records to the correct tenant, record and schema while detecting tampering?', exact=True).click()
    page.wait_for_function('window.GuideAppReady === true')
    encryption = page.locator(page.evaluate('location.hash'))
    assert encryption.locator('details.answer').get_attribute('open') is not None
    assert 'cryptography dependency required' in encryption.locator('.question-code').inner_text()
    assert 'AESGCM' in encryption.locator('pre code').first.inner_text()
    assert encryption.locator('.answer-diagram').count() == 1
    page.goto(base + '/classification.html')
    page.wait_for_function('window.GuideAppReady === true')
    assert page.locator('article[data-question]').count() == 18
    page.get_by_role('link', name='Download text_grouping_lab.py', exact=True).wait_for()
    assert page.get_by_role('link', name='Download text_grouping_lab.py', exact=True).get_attribute('href').endswith('examples/labs/text_grouping_lab.py')
    page.goto(base + '/clustering.html')
    page.wait_for_function('window.GuideAppReady === true')
    assert page.locator('article[data-question]').count() == 18
    assert page.locator('.answer-diagram').count() == 16
    print(json.dumps({'learning_navigation':'pass','scenario_questions':scenario_count,'mobile_overflow':False}))

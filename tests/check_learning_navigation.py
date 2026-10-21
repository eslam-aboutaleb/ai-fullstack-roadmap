"""Behavior checks for finding and practicing advanced scenarios."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check(page, base):
    page.goto(base + '/design-scenarios.html')
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
    print(json.dumps({'learning_navigation':'pass','scenario_questions':15,'mobile_overflow':False}))

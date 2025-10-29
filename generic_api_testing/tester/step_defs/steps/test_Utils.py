from pytest_bdd import parsers, given, when, then

@given(parsers.cfparse(u'the test has ID "{test_ID}"'))
@when(parsers.cfparse(u'the test has ID "{test_ID}"'))
@then(parsers.cfparse(u'the test has ID "{test_ID}"'))
def store_test_id(test_ID):
    test_ID = test_ID
import seasons
import pytest
import datetime

LONDON = (51.507351, -0.127758)
MURMANSK = (68.958524, 33.08266)
BUENOSAIRES = (-34.603684, -58.381559)
MELBOURNE = (-37.813628, 144.963058)
PONTIANAK = (0.0, -109.20)


class TestLocation:
    @pytest.mark.parametrize(('lat', 'lng', 'expected'), [
        (*LONDON, 'northern'),
        (*MURMANSK, 'northern'),
        (*BUENOSAIRES, 'southern'),
        (*MELBOURNE, 'southern'),
        (*PONTIANAK, 'southern'),
    ])
    def test_hemisphere(self, lat, lng, expected):
        loc = seasons.Location(lat, lng)
        assert loc.hemisphere == expected

    @pytest.mark.parametrize(('lat', 'lng', 'expected'), [
        (*LONDON, 'UK'),
        (*MURMANSK, 'Russian Federation'),
        (*BUENOSAIRES, 'Argentina'),
        (*MELBOURNE, 'Australia'),
        (*PONTIANAK, None),  # seems rough
    ])
    def test_country(self, lat, lng, expected):
        loc = seasons.Location(lat, lng)
        assert loc.country == expected


class TestSeason:
    def test_valid_for(self):
        """For southern_meteo, 3 july
        """
        july = datetime.date(1983, 7, 3)
        result = {(s.name, s.valid_for(july))
                   for s in seasons.southern_meteo.seasons}
        expected = {('spring', False),
                    ('summer', False),
                    ('autumn', False),
                    ('winter', True)
        }
        assert result == expected


class TestSeasonset:
    @pytest.mark.parametrize(('seasonset', 'expected'), [
        (seasons.northern_meteo, 'summer'),
        (seasons.northern_astro, 'summer'),
        (seasons.southern_meteo, 'winter'),
        (seasons.southern_astro, 'winter'),
    ])
    def test_get_season_3_july(self, seasonset, expected):
        date = datetime.date(1983, 7, 3)
        assert seasonset.get_season(date) == expected

    @pytest.mark.parametrize(('seasonset', 'expected'), [
        (seasons.northern_meteo, 'spring'),
        (seasons.northern_astro, 'winter'),
        (seasons.southern_meteo, 'autumn'),
        (seasons.southern_astro, 'summer'),
    ])
    def test_get_season_19_march(self, seasonset, expected):
        """This date falls between the astronomical and meteorological seasons
        """
        date = datetime.date(2017, 3, 19)
        assert seasonset.get_season(date) == expected

    @pytest.mark.parametrize(('loc', 'seasonset', 'expected'), [
        (LONDON, seasons.northern_meteo, True),
        (LONDON, seasons.northern_astro, True),
        (LONDON, seasons.southern_meteo, False),
        (LONDON, seasons.southern_meteo, False),
    ])
    def test_valid_for(self, loc, seasonset, expected):
        location = seasons.Location(*loc)
        assert seasonset.valid_for(location) == expected


def test_astronomical_dates():
    result = seasons.astronomical_dates(2017)
    expected = {'dec': datetime.date(2017, 12, 21),
                'june': datetime.date(2017, 6, 21),
                'sept': datetime.date(2017, 9, 22),
                'march': datetime.date(2017, 3, 20)}
    assert result == expected


def test_between_equinoxes():
    dates = seasons.astronomical_dates(2017)
    july = datetime.date(2017, 7, 3)
    assert seasons.between_equinoxes(july, 'march', 'sept')
    assert seasons.between_equinoxes(july, 'march', 'dec')
    assert seasons.between_equinoxes(july, 'june', 'sept')
    assert seasons.between_equinoxes(july, 'june', 'dec')
    assert seasons.between_equinoxes(july, 'march', None)
    assert seasons.between_equinoxes(july, 'june', None)
    assert seasons.between_equinoxes(july, None, 'sept')
    assert seasons.between_equinoxes(july, None, 'dec')
    assert not seasons.between_equinoxes(july, 'march', 'june')
    assert not seasons.between_equinoxes(july, 'sept', 'dec')
    assert not seasons.between_equinoxes(july, None, 'march')
    assert not seasons.between_equinoxes(july, None, 'june')
    assert not seasons.between_equinoxes(july, 'sept', None)
    assert not seasons.between_equinoxes(july, 'dec', None)


def test_between_dates():
    july = datetime.date(2017, 7, 3)
    assert seasons.between_dates(july, (7, 3), (7, 4))
    assert not seasons.between_dates(july, (7, 2), (7, 3))
    assert seasons.between_dates(july, (7, 3), None)
    assert seasons.between_dates(july, None, (7, 4))

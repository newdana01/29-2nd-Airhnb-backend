from django.test    import TestCase, Client

from users.models  import User
from houses.models import City, Country, Ghost, House, HouseType

class HouseListTest(TestCase):
    def setUp(self):
        Country.objects.create(id=1, name="test_country1")
        City.objects.bulk_create(
            [
                City(id=1, name="test_city1", country_id=1),
                City(id=2, name="test_city2", country_id=1),
            ]
        )
        HouseType.objects.bulk_create(
            [
                HouseType(id=1, name="test_type1"),
                HouseType(id=2, name="test_type2")
            ]
        )
        House.objects.bulk_create(
            [
                House(id=1, name="test1", description="desc1", max_guest=5, city_id=1, house_type_id=1),
                House(id=2, name="test2", description="desc2", max_guest=5, city_id=1, house_type_id=1),
                House(id=3, name="test3", description="desc3", max_guest=5, city_id=2, house_type_id=2)
            ]
        )
    
    def tearDown(self):
        Country.objects.all().delete()
        City.objects.all().delete()
        HouseType.objects.all().delete()
        House.objects.all().delete()

    def test_get_all_house_list_success(self):
        client = Client()

        response = client.get('/houses')

        self.assertEqual(len(response.json()["results"]), 3)
        self.assertEqual(response.json()["results"][0]["name"], "test1")
        self.assertEqual(response.json()["results"][1]["name"], "test2")
        self.assertEqual(response.json()["results"][2]["name"], "test3")
        self.assertEqual(response.status_code, 200)

    def test_get_house_list_with_city_option_success(self):
        client = Client()

        response = client.get('/houses?city=test_city1')

        self.assertEqual(len(response.json()["results"]), 2)
        self.assertEqual(response.json()["results"][0]["city"], "test_city1")
        self.assertEqual(response.json()["results"][1]["city"], "test_city1")
        self.assertEqual(response.status_code, 200)


class HostTest(TestCase):
    def setUp(self):
        test_user = User.objects.create(
                id                  = 1,
                name                = "test",
                email               = "test@kakao.com",
                password            = "123456789",
                phone_number        = "010-0000-0000",
                profile_image_url   = "test_url",
                kakao_id            = "test_kakao_id",
                google_id           = "test_google_id",
                birth_date          = "1999-01-01"
            )

        test_country    = Country.objects.create(name="test_country")
        test_city       = City.objects.create(name="test_city", country_id=test_country.id)
        test_house_type = HouseType.objects.create(name="test_house_type")
        test_ghost      = Ghost.objects.create(name="test_ghost")

        House.objects.create(
            id          = 1,
            name        = "test",
            description = "test_text",
            latitude    = 12.3456,
            logitude    = 98.7654,
            max_guest   = "5",
            trap        = True,
            exit        = False,
            city        = test_city,
            house_type  = test_house_type,
            ghost       = test_ghost,
            user        = test_user,
        )

    def tearDown(self):
        User.objects.all().delete()
        Country.objects.all().delete()
        City.objects.all().delete()
        HouseType.objects.all().delete()
        Ghost.objects.all().delete()
        House.objects.all().delete()


    

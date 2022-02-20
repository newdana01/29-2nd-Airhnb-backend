from decimal import Decimal

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q, Count, Avg

from houses.models import (
                            Country,
                            House,
                            City,
                            HouseTypeEnum,
                            GhostEnum
                            )

class OptionView(View):
    def get(self, request):
        results = [
            {
                'house_type': [house_type.name for house_type in HouseTypeEnum]
            },
            {
                'ghost': [ghost.name for ghost in GhostEnum]
            },
            {
                'country': [country.name for country in Country.objects.all()]
            },
            {
                'city': [city.name for city in City.objects.all()]
            }
        ]

        return JsonResponse({'results': results}, status=200)

class HouseView(View):
    def get(self, request):
        house_type  = request.GET.getlist('house_type',None)
        ghost       = request.GET.getlist('ghost',None)
        country     = request.GET.getlist('country',None)
        city        = request.GET.getlist('city', None)
        trap        = request.GET.get('trap', None)
        exit        = request.GET.get('exit', None)
        check_in    = request.GET.get('check_in', None)
        check_out   = request.GET.get('check_out', None)
        headcount   = request.GET.get('headcount', None)
        # latitude    = Decimal(request.GET.get('lat'))
        # longitude   = Decimal(request.GET.get('lng'))
        limit       = int(request.GET.get('limit', '10'))
        offset      = int(request.GET.get('offset', '0'))

        filter_options = {
            'house_type': 'house_type__name__in',
            'ghost'     : 'ghost__name__in',
            'country'   : 'city__country__name__in',
            'city'      : 'city__name__in',
            'trap'      : 'trap__in',
            'exit'      : 'exit__in',
            # 'check_in'  : 'reservation__check_in__range',
            # 'check_out' : 'reservation__check_in__gt',
            'headcount' : 'max_guest__lt',
        }

        filter_set = {
            filter_options.get(key): value[0] for (key, value) in dict(request.GET).items() if filter_options.get(key)
        }

        options     = Q()
        reservation = Q()

        

        if house_type:
            options &= Q(house_type__name__in=house_type)
        if ghost:
            options &= Q(ghost__name__in=ghost)
        if country:
            options &= Q(city__country__name__in=country)
        if city:
            options &= Q(city__name__in=city)
        if trap:
            options &= Q(trap=trap)
        if exit:
            options &= Q(exit=exit)
        # if latitude and longitude:
        #     options &= Q(__range=(latitude, longitude))
        if check_in:
            reservation &= Q(reservation__check_in__range=(check_in, check_out))
        if check_out:
            reservation &= Q(reservation__check_in__gt=check_in)
        if check_out:
            reservation &= Q(reservation__check_in__lte=check_out)
        if headcount:
            reservation &= Q(max_guest__lt=headcount)

        houses = House.objects.filter(options, ~reservation)\
                        .select_related('user')\
                        .select_related('ghost')\
                        .prefetch_related('houseimage_set')\
                        .prefetch_related('review_set')

        results = [
            {
                'house_id'        : house.id,
                'name'            : house.name,
                'house_image'     : [image.image_url for image in house.houseimage_set.all()],
                'lat'             : house.latitude,
                'lng'             : house.longitude,
                'user_name'       : house.user.name if house.user else None,
                'review_average'  : house.review_set.aggregate(total=Avg('fear_rating')),
                'review_count'    : house.review_set.aggregate(total=Count('fear_rating')),
                'trap'            : house.trap,
                'exit'            : house.exit,
                'ghost'           : house.ghost.name if house.ghost else None,
                'city'            : house.city.name,
                'country'         : house.city.country.name,
                'house_type'      : house.house_type.name
            } for house in houses[offset:offset+limit]
        ]

        total_pages = houses.aggregate(total=Count('name'))['total']

        return JsonResponse({
            'results'    : results,
            'total_pages': total_pages
            },
            status=200)
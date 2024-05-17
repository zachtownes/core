"""Interact with Tandoor Meal Plan."""

import datetime
import logging
from zoneinfo import ZoneInfo

import requests

_LOGGER = logging.getLogger(__name__)


class Tandoor:
    """Tandoor webui class."""

    def __init__(self, url, api_key) -> None:  # noqa: D107
        self._url = url
        self._api_key = api_key
        self._meal_plan = None
        self._recipe_name = None
        self._recipe_id = None
        self._servings = None
        self._note = None
        self._recipe_image = None
        self._recipe_url = None

    @property
    def url(self):  # noqa: D102
        return self._url

    @property
    def api_key(self):  # noqa: D102
        return self._api_key

    def tandoor_test(url, api_key):  # noqa: N805
        """Test Tandoor webui."""
        _LOGGER.debug("Tandoor test started")
        response = requests.get(
            f"{url}/api/", headers={"Authorization": f"Bearer {api_key}"}, timeout=10
        )
        response.raise_for_status()
        return response.json()

    def get_today_meal_plan(url, api_key, time_zone):  # noqa: N805
        """Get today's meal plan."""
        _LOGGER.debug("Getting today's meal plan")
        my_date = datetime.datetime.now(ZoneInfo(time_zone))
        today = my_date.strftime("%Y-%m-%d")
        _LOGGER.debug(today)
        response = requests.get(
            f"{url}/api/meal-plan/?from_date={today}&to_date={today}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        response.raise_for_status()
        meal_plan = response.json()
        if meal_plan:
            meal = meal_plan[0]  # assuming you're interested in the first meal plan
            if meal.get("recipe"):
                recipe_name = meal.get("recipe", {}).get("name")
                recipe_id = meal.get("recipe", {}).get("id")
                recipe_image = meal.get("recipe", {}).get("image")
                servings = meal.get("servings")
                note = meal.get("note")
                recipe_url = f"{url}/view/recipe/{recipe_id}?servings={servings}"
                recipeObject = {
                    "recipe_name": recipe_name,
                    "recipe_id": recipe_id,
                    "recipe_image": recipe_image,
                    "servings": servings,
                    "note": note,
                    "recipe_url": recipe_url,
                }
            else:
                recipe_name = meal.get("title")
                servings = meal.get("servings")
                note = meal.get("note")
                recipe_id = None
                recipe_image = None
                recipe_url = "https://recipes.mysticturtles.com/plan/"

                recipeObject = {
                    "recipe_name": recipe_name,
                    "servings": servings,
                    "note": note,
                    "recipe_id": recipe_id,
                    "recipe_image": recipe_image,
                    "recipe_url": recipe_url,
                }
        else:
            recipe_name = "No meal plan"
            servings = None
            note = None
            recipe_id = None
            recipe_image = None
            recipe_url = None
            recipeObject = {
                "recipe_name": recipe_name,
                "servings": servings,
                "note": note,
                "recipe_id": recipe_id,
                "recipe_image": recipe_image,
                "recipe_url": recipe_url,
            }
        return recipeObject

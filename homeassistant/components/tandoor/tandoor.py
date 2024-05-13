import datetime  # noqa: D100
import logging

import aiohttp

LOGGER = logging.getLogger(__name__)


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

    async def tandoor_test(self, url, api_key):
        """Test Tandoor webui."""
        LOGGER.debug("Tandoor test started")
        async with aiohttp.ClientSession() as session:  # noqa: SIM117
            async with session.get(
                f"{url}/api/",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            ) as response:
                if response.status == 200:
                    LOGGER.debug("Tandoor test passed")
                    return True
                else:  # noqa: RET505
                    LOGGER.debug("Tandoor test failed")
                    return False

    async def get_today_meal_plan(self, url, api_key):
        """Get today's meal plan."""
        LOGGER.debug("Getting today's meal plan")
        today = datetime.date.today().strftime("%Y-%m-%d")
        async with aiohttp.ClientSession() as session:  # noqa: SIM117
            async with session.get(
                f"{url}/api/meal-plan/?from_date={today}&to_date={today}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            ) as response:
                if response.status == 200:
                    self._meal_plan = await response.json()
                    if self._meal_plan:
                        meal_plan = self._meal_plan[
                            0
                        ]  # assuming you're interested in the first meal plan
                        if meal_plan.get("recipe"):
                            self._recipe_name = meal_plan.get("recipe", {}).get("name")
                            self._recipe_id = meal_plan.get("recipe", {}).get("id")
                            self._recipe_image = meal_plan.get("recipe", {}).get(
                                "image"
                            )
                            self._servings = meal_plan.get("servings")
                            self._note = meal_plan.get("note")
                            self._recipe_url = f"{url}/view/recipe/{self._recipe_id}?servings={self._servings}"
                        elif self._meal_plan:
                            meal_plan = self._meal_plan[
                                0
                            ]  # assuming you're interested in the first meal plan
                            self._recipe_name = meal_plan.get("title")
                            self._servings = meal_plan.get("servings")
                            self._note = meal_plan.get("note")
                            self._recipe_id = None
                            self._recipe_image = None
                            self._recipe_url = "https://recipes.mysticturtles.com/plan/"
                        return self
                else:
                    return None

from django.db import models
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default="")
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["id"]

    def __str__(self):
        return self.name

    def better_name(self):
        name = self.name
        name = (
            name.removeprefix("Faculté de ")
            .removeprefix("Faculté d'")
            .removeprefix("Faculté des ")
        )
        name = name.replace(
            "Agrégation de l'enseignement secondaire supérieur", "Agrégation"
        ).replace(
            "Certificat d'aptitude pédagogique approprié à l'enseignement supérieur",
            "Certificat",
        )
        name = name.removeprefix("Bachelier en ").removeprefix("Bachelier : ")
        name = (
            name.removeprefix("Master en ")
            .removeprefix("Master : ")
            .removeprefix("Master de ")
        )
        if "orientation" in name:
            name = name.replace("orientation générale", "orientation Général").replace(
                "orientation ", "("
            ) + ")".replace("Général à finalité", "")
        rr = {
            "Haute Ecole Libre de Bruxelles": "HELB",
            "Institut des Hautes Etudes des Communications Sociales": "IHECS",
            "Solvay": "Solvay",
        }
        for k, v in rr.items():
            if k in name:
                name = v
        return name


class Course(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    categories = models.ManyToManyField(Category)
    description = models.TextField(default="")

    followed_by = models.ManyToManyField("users.User", related_name="courses_set")

    class Meta:
        ordering = ["slug"]

    def gehol_url(self):
        slug = self.slug.replace("-", "").upper()
        return f"https://gehol.ulb.ac.be/gehol/Vue/HoraireCours.php?cours={slug}"

    def get_absolute_url(self):
        return reverse("catalog:course_show", args=(self.slug,))

    def __str__(self):
        return self.slug.upper()

    def fullname(self):
        return f"{self.name} ({self.slug.lower()})"

    @property
    def followers_count(self) -> int:
        return self.followed_by.count()

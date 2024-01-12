from golf_course import GolfCourse
from graph_utils import find_best_path, visualize_course

def main():
    golf_course = GolfCourse()

    # Ajouter le point de départ (Tee) et le point d'arrivée (Trou)
    golf_course.add_tee("Tee1", (0, 0))
    golf_course.add_hole("Hole1", (10, 10))

    # Ajouter des obstacles
    golf_course.add_obstacle("Tree1", (4, 5), "tree")
    golf_course.add_obstacle("Bunker1", (6, 7), "bunker")
    golf_course.add_obstacle("Water1", (2, 8), "water")

    # Ajouter des coups possibles (Tee -> Obstacles -> Hole)
    golf_course.add_shot("Tee1", "Tree1", 1)
    golf_course.add_shot("Tree1", "Bunker1", 1)
    golf_course.add_shot("Bunker1", "Hole1", 1)

    # Pour un test plus réaliste, vous pouvez ajouter des coups alternatifs
    golf_course.add_shot("Tee1", "Bunker1", 2)  # Un coup direct, mais plus difficile
    golf_course.add_shot("Tee1", "Water1", 1)   # Un autre chemin possible
    golf_course.add_shot("Water1", "Hole1", 3)  # Un chemin avec plus de difficulté

    # Visualiser le parcours
    visualize_course(golf_course)

    # Trouver le meilleur parcours du Tee au Trou
    best_path = find_best_path(golf_course.graph, "Tee1", "Hole1")

    # Afficher le meilleur parcours
    print(f"Meilleur parcours: {best_path}")

if __name__ == "__main__":
    main()

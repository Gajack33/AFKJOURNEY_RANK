# Guide de Contribution

Merci de votre intérêt pour contribuer à AFK Journey Rank Tracker ! Voici quelques directives pour vous aider à contribuer au projet.

## Comment contribuer

1. Fork le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Standards de code

- Suivez le style de code [Black](https://github.com/psf/black)
- Ajoutez des docstrings pour toutes les fonctions et classes
- Commentez votre code quand nécessaire
- Écrivez des messages de commit clairs et descriptifs

## Tests

- Ajoutez des tests pour toute nouvelle fonctionnalité
- Assurez-vous que tous les tests passent avant de soumettre une PR
- Utilisez pytest pour les tests

## Documentation

- Mettez à jour la documentation pour refléter vos changements
- Documentez les nouvelles fonctionnalités dans le README.md
- Ajoutez des exemples d'utilisation si nécessaire

## Rapport de bugs

- Utilisez le système d'issues de GitHub
- Incluez les étapes pour reproduire le bug
- Mentionnez votre environnement (OS, version Python, etc.)
- Ajoutez des captures d'écran si pertinent

## Suggestions de fonctionnalités

- Vérifiez d'abord que la fonctionnalité n'existe pas déjà
- Expliquez clairement le besoin et l'utilité
- Proposez une implémentation si possible

## Structure des commits

Format recommandé pour les messages de commit :
```
type(scope): description courte

Description détaillée si nécessaire
```

Types :
- feat: nouvelle fonctionnalité
- fix: correction de bug
- docs: documentation
- style: formatage
- refactor: refactoring
- test: ajout/modification de tests
- chore: maintenance

## Branches

- `main` : branche principale, stable
- `develop` : branche de développement
- `feature/*` : nouvelles fonctionnalités
- `fix/*` : corrections de bugs
- `docs/*` : documentation

## Questions

Si vous avez des questions, n'hésitez pas à :
1. Consulter la documentation existante
2. Ouvrir une issue avec le label "question"
3. Contacter les mainteneurs

## Licence

En contribuant, vous acceptez que vos contributions soient sous la même licence que le projet (MIT). 
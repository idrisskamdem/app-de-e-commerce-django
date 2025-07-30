from django.db import models
from django.db.models import Sum, F, DecimalField
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Utilisateur(AbstractUser):
    adresse=models.CharField(max_length=255,blank=True,null=True)
    photo_profil=models.ImageField(upload_to='profils/', blank=True,null=True)

    def __str__(self):
        return self.username
# modele pour le client

class Client(Utilisateur):
    historique_commandes=models.ManyToManyField('Commande', blank=True, related_name='client_historique')

    def __str__(self):
        return self.username

# modele pour l'administrateur

class Admin(Utilisateur):
    class Meta:
        proxy=True
    def __str__(self):
        return self.username
# modele pour categorie

class Categorie(models.Model):
    nom=models.CharField(max_length=100)
    description=models.TextField(blank=True,null=True)
    
    def __str__(self):
        return self.nom

# modele pour le produit

class Produit(models.Model):
    nom=models.CharField(max_length=100)
    description=models.TextField()
    prix=models.DecimalField(max_digits=100,decimal_places=2)
    stock=models.IntegerField()
    categorie=models.ForeignKey(Categorie,on_delete=models.CASCADE,related_name='produits')
    photo=models.ImageField(upload_to='produit/',blank=True,null=True)

    def est_disponible(self):
        return self.stock >0 
    def __str__(self):
        return self.nom
    def calculer_note_moyenne(self):
        return self.avis.aggregate(moyenne=Avg('note'))['moyenne'] or 0   

# modele pour le panier


class Panier(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='panier')
    produits = models.ManyToManyField(Produit, through='LignePanier')

    def __str__(self):
        return f"panier de {self.client.username}"

    def calculer_total(self):
       total = sum(ligne.sous_total() for ligne in self.lignepanier_set.all())
       return total or 0

    def est_vide(self):
        return self.lignepanier_set.count() == 0


# modele pour lignepanier

class LignePanier(models.Model):
    panier=models.ForeignKey(Panier,on_delete=models.CASCADE)
    produit=models.ForeignKey(Produit,on_delete=models.CASCADE)
    quantite=models.IntegerField(default=1)

    def sous_total(self):
        return self.produit.prix * self.quantite
    def __str__(self):
        return f"{self.quantite}x {self.produit.nom}" 

# modele pour la commande


class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes')
    produit = models.ManyToManyField(Produit, through='LigneCommande')
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=[('en_cours', 'En cours'), ('livre', 'Livre'), ('annule', 'Annule'),])

    def __str__(self):
        return f"commande #{self.id} par {self.client.username}"

    def calculer_total(self):
        # Ajout de output_field pour spécifier le type du résultat
        return self.lignecommande_set.aggregate(
            total=Sum(F('quantite') * F('produit__prix'), output_field=DecimalField())
        )['total'] or 0
    def total_commande(self):
        return sum([ligne.sous_total() for ligne in self.lignecommande_set.all()])    


# modele pour la ligneCommande

class LigneCommande(models.Model):
    commande=models.ForeignKey(Commande,on_delete=models.CASCADE)
    produit=models.ForeignKey(Produit,on_delete=models.CASCADE)
    quantite=models.IntegerField(default=1)

    def sous_total(self):
        return self.produit.prix * self.quantite
    def __str__(self):
        return f"{self.quantite}X {self.produit.nom}"
#modele pour le paiment

class Paiement(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='paiement')
    montant=models.DecimalField(max_digits=10,decimal_places=2)
    methode=models.CharField(max_length=50,choices=[('carte','Carte de credit'),('Paypal','Paypal'),])
    statut=models.CharField(max_length=50,choices=[('reussi','Reussi'),('echoue','Echoue'),]) 

    def __str__(self):
        return f"paiement pour la commande #{self.commande.id}"

# modele pour les avis 

class Avis(models.Model):
    produit=models.ForeignKey(Produit,on_delete=models.CASCADE,related_name='avis')
    client=models.ForeignKey(Client,on_delete=models.CASCADE,related_name='avis')
    note=models.IntegerField(choices=[(i,i) for i in range(1,6)])
    commentaire=models.TextField()
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avis de {self.client.username} sur {self.produit.nom}"

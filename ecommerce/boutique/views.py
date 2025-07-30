from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Sum, F,Avg
from .models import *
from .forms import AvisForm, PaiementForm, LignePanierForm, ClientRegistrationForm, ClientUpdateForm

# Fonction pour créer un client pour un utilisateur
def create_client_for_user(user):
    if not hasattr(user, 'client'):
        client = Client.objects.create(user=user)
        user.client = client
        user.save()

# Vues produits
def home(request):
    return render(request, 'boutique/base.html')

def liste_produits(request):
    produits = Produit.objects.filter(stock__gt=0)#.select_related('categorie')
    return render(request, 'boutique/produits/liste_produits.html', {
        'produits': produits,
        'panier_count': Panier.objects.filter(client=request.user.client).first().lignepanier_set.count() if hasattr(request.user, 'client') else 0
    })

def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    
    # Vérifie si le produit a des avis pour éviter une erreur
    #note_moyenne = produit.avis.aggregate(moyenne=Avg('note'))['moyenne']
    
    context = {
        'produit': produit,
        'note_moyenne': note_moyenne if note_moyenne is not None else 0,  # Assurez-vous qu'il y a une valeur
    }
    print(context)  # 🔍 Vérifie le contenu du contexte dans la console
    return render(request, 'boutique/produits/detail_produit.html', context)


# Vues panier

# Fonction pour créer un client pour un utilisateur
def create_client_for_user(user):
    if not Client.objects.filter(id=user.id).exists():
        Client.objects.create(
            id=user.id,  # Assure que le Client partage le même ID que l'Utilisateur
            username=user.username,
            email=user.email,
            adresse=user.adresse,
        )
        '''except IntegrityError as e:
            # Cela pourrait être utile si tu as une contrainte d'unicité en base de données qui est violée
            print(f"Erreur lors de la création du client : {e}")
            messages.error(user, "Une erreur est survenue lors de la création de votre profil.")'''

# Puis, dans la fonction de gestion du panier
@login_required
def gestion_panier(request):
    if not hasattr(request.user, 'client'):
        messages.error(request, "Vous devez être un client pour accéder au panier.")
        return redirect('home')

    panier, created = Panier.objects.get_or_create(client=request.user.client)
    
    return render(request, 'boutique/panier/panier.html', {
        'panier': panier,
        'total': panier.lignepanier_set.aggregate(
            total=Sum(F('quantite') * F('produit__prix'))
        )['total'] or 0
    })


@login_required
def ajouter_au_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    
    if produit.stock < 1:
        messages.error(request, "Ce produit est en rupture de stock")
        return redirect('liste_produits')
    
    panier = request.user.client.panier
    ligne, created = panier.lignepanier_set.get_or_create(
        produit=produit,
        defaults={'quantite': 1}
    )
    
    if not created:
        if ligne.quantite + 1 > produit.stock:
            messages.error(request, "Stock insuffisant")
            return redirect('gestion_panier')
        ligne.quantite += 1
        ligne.save()
    
    messages.success(request, f"{produit.nom} ajouté au panier")
    return redirect('detail_produit', produit_id=produit_id)

@login_required
def retirer_du_panier(request, ligne_id):
    ligne = get_object_or_404(LignePanier, id=ligne_id, panier__client=request.user.client)
    ligne.delete()
    messages.success(request, "Article retiré du panier")
    return redirect('gestion_panier')

# Vues commandes
@login_required
@transaction.atomic
def passer_commande(request):
    client = request.user.client
    panier = client.panier
    
    if not panier.lignepanier_set.exists():
        messages.warning(request, "Votre panier est vide")
        return redirect('liste_produits')
    
    # Vérification stock
    for ligne in panier.lignepanier_set.all():
        if ligne.produit.stock < ligne.quantite:
            messages.error(request, f"Stock insuffisant pour {ligne.produit.nom}")
            return redirect('gestion_panier')
    
    # Création commande
    commande = Commande.objects.create(client=client, statut='en_cours')
    
    # Transfert panier vers commande
    for ligne in panier.lignepanier_set.all():
        LigneCommande.objects.create(
            commande=commande,
            produit=ligne.produit,
            quantite=ligne.quantite
        )
        # Mise à jour stock
        ligne.produit.stock -= ligne.quantite
        ligne.produit.save()
    
    panier.lignepanier_set.all().delete()
    
    return redirect('paiement', commande_id=commande.id)

@login_required
def suivi_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client=request.user.client)
    return render(request, 'boutique/suivi_commande.html', {'commande': commande})

# Vues paiement
@login_required
def paiement(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client=request.user.client)
    
    if hasattr(commande, 'paiement'):
        return redirect('suivi_commande', commande_id=commande_id)
    
    total = commande.lignecommande_set.aggregate(
        total=Sum(F('quantite') * F('produit__prix'))
    )['total'] or 0
    
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.commande = commande
            paiement.montant = total
            paiement.statut = 'réussi'  # À remplacer par intégration réelle
            paiement.save()
            
            commande.statut = 'livré'
            commande.save()
            
            messages.success(request, "Paiement effectué avec succès !")
            return redirect('suivi_commande', commande_id=commande_id)
    else:
        form = PaiementForm()
    
    return render(request, 'boutique/paiement.html', {
        'commande': commande,
        'total': total,
        'form': form
    })

# Vues avis
@login_required
def laisser_avis(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    client = request.user.client
    
    # Vérifier si le client a déjà commandé le produit
    if not LigneCommande.objects.filter(commande__client=client, produit=produit).exists():
        messages.warning(request, "Vous devez avoir commandé ce produit pour laisser un avis")
        return redirect('detail_produit', produit_id=produit_id)
    
    avis_existant = Avis.objects.filter(client=client, produit=produit).first()
    
    if request.method == 'POST':
        form = AvisForm(request.POST, instance=avis_existant)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.client = client
            avis.produit = produit
            avis.save()
            messages.success(request, "Avis enregistré !")
            return redirect('detail_produit', produit_id=produit_id)
    else:
        form = AvisForm(instance=avis_existant)
    
    return render(request, 'boutique/avis.html', {'form': form, 'produit': produit})

def about_us(request):
    return render(request, 'boutique/about-us.html')

def contact_us(request):
    if request.method == 'POST':
        messages.success(request, "Votre message a été envoyé avec succès !")
        return redirect('contact_us')
    return render(request, 'boutique/contact-us.html') 

def commande_detail(request, commande_id):
    commande = Commande.objects.get(id=commande_id)
    return render(request, 'commande.html', {'commande': commande}) 

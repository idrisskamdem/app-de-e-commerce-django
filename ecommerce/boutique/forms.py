# boutique/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.Select(choices=[(i, f'{i} étoile{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'commentaire': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Partagez votre expérience avec ce produit...'
            }),
        }
        labels = {
            'note': 'Note (entre 1 et 5)',
            'commentaire': 'Commentaire'
        }

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['methode']
        widgets = {
            'methode': forms.RadioSelect(choices=Paiement._meta.get_field('methode').choices)
        }
        labels = {
            'methode': 'Méthode de paiement'
        }

class LignePanierForm(forms.ModelForm):
    class Meta:
        model = LignePanier
        fields = ['quantite']
        widgets = {
            'quantite': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control',
                'style': 'width: 70px;'
            })
        }

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    adresse = forms.CharField(max_length=255, required=True)
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password1', 'password2', 'adresse']

class ClientUpdateForm(UserChangeForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'adresse', 'photo_profil']
        exclude = ['password']

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields=['nom','description','prix','stock','categorie','photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'prix': forms.NumberInput(attrs={'step': 0.01}),
            'stock': forms.NumberInput(attrs={'min': 0}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'})
        }
        help_texts = {
            'stock': 'Quantité disponible en inventaire',
            'disponible': 'Cocher si le produit est visible sur le site'
        }
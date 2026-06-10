import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProfileService } from '../../services/profile.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.html',
  styleUrls: ['./profile.css'],
})
export class ProfilePage implements OnInit {
  user: any = null;
  form: any = { first_name: '', last_name: '', email: '', username: '' };
  passwordForm = { old_password: '', new_password: '', new_password2: '' };
  isLoading = false;
  feedback = '';
  feedbackType: 'success' | 'error' = 'success';

  constructor(private profileService: ProfileService) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  get initials(): string {
    if (!this.user) return '';
    return `${(this.user.first_name || '?')[0]}${(this.user.last_name || '?')[0]}`.toUpperCase();
  }

  loadProfile(): void {
    this.isLoading = true;
    this.profileService.getCurrentUser().subscribe({
      next: (response) => {
        this.user = response;
        this.form = {
          first_name: response.first_name || '',
          last_name: response.last_name || '',
          email: response.email || '',
          username: response.username || '',
        };
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.feedbackType = 'error';
        this.feedback = 'Impossible de charger le profil. Veuillez vous reconnecter.';
      },
    });
  }

  saveProfile(): void {
    this.isLoading = true;
    this.profileService.updateCurrentUser(this.form).subscribe({
      next: () => {
        this.isLoading = false;
        this.feedbackType = 'success';
        this.feedback = '✅ Profil mis à jour avec succès.';
        this.loadProfile();
      },
      error: () => {
        this.isLoading = false;
        this.feedbackType = 'error';
        this.feedback = 'Erreur lors de la mise à jour du profil.';
      },
    });
  }

  changePassword(): void {
    this.isLoading = true;
    this.profileService.changePassword(
      this.passwordForm.old_password,
      this.passwordForm.new_password,
      this.passwordForm.new_password2,
    ).subscribe({
      next: () => {
        this.isLoading = false;
        this.feedbackType = 'success';
        this.feedback = '✅ Mot de passe mis à jour.';
        this.passwordForm = { old_password: '', new_password: '', new_password2: '' };
      },
      error: () => {
        this.isLoading = false;
        this.feedbackType = 'error';
        this.feedback = 'Erreur de mot de passe. Vérifiez les champs.';
      },
    });
  }
}
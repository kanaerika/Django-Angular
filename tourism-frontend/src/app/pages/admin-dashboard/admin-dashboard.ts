import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AdminService } from '../../services/admin.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './admin-dashboard.html',
  styleUrls: ['./admin-dashboard.css'],
})
export class AdminDashboard implements OnInit {
  tab: 'stats' | 'users' | 'reviews' | 'bookings' | 'create' = 'stats';

  stats: any = null;
  users: any[] = [];
  reviews: any[] = [];
  bookings: any[] = [];
  cities: any[] = [];
  categories: any[] = [];

  feedback = '';
  feedbackType: 'success' | 'error' = 'success';

  newActivity: any = { title: '', city: null, description: '', base_price: null, max_travelers: 10, duration_hours: 2, categories: [], is_active: true };
  newSchedule: any = { activity: null, date: '', start_time: '10:00:00', available_spots: 10 };
  activities: any[] = [];

  bookingStatuses = ['pending', 'confirmed', 'completed', 'cancelled', 'refunded'];

  constructor(private admin: AdminService) {}

  ngOnInit(): void { this.openTab('stats'); }

  openTab(tab: any): void {
    this.tab = tab;
    this.feedback = '';
    if (tab === 'stats') this.admin.getStats().subscribe({ next: (s) => this.stats = s, error: () => this.error('Stats inaccessibles (êtes-vous admin ?)') });
    if (tab === 'users') this.admin.listUsers().subscribe({ next: (r: any) => this.users = r?.results ?? r, error: () => this.error('Liste utilisateurs réservée aux admins.') });
    if (tab === 'reviews') this.admin.pendingReviews().subscribe({ next: (r: any) => this.reviews = r?.results ?? r, error: () => this.error('Avis en attente inaccessibles.') });
    if (tab === 'bookings') this.admin.listBookings().subscribe({ next: (r: any) => this.bookings = r?.results ?? r, error: () => this.error('Réservations inaccessibles.') });
    if (tab === 'create') {
      this.admin.listCities().subscribe({ next: (r: any) => this.cities = r?.results ?? r });
      this.admin.listCategories().subscribe({ next: (r: any) => this.categories = r?.results ?? r });
    }
  }

  assignRole(user: any, roleId: string): void {
    this.admin.assignRole(user.id, Number(roleId)).subscribe({
      next: () => { this.success(`Rôle mis à jour pour ${user.email}.`); this.openTab('users'); },
      error: () => this.error('Impossible de changer le rôle.'),
    });
  }

  moderate(review: any, visible: boolean): void {
    this.admin.moderateReview(review.id, visible).subscribe({
      next: () => { this.success(visible ? 'Avis approuvé.' : 'Avis rejeté.'); this.openTab('reviews'); },
      error: () => this.error('Modération impossible.'),
    });
  }

  setStatus(booking: any, status: string): void {
    this.admin.setBookingStatus(booking.id, status).subscribe({
      next: () => { this.success(`Réservation ${booking.booking_reference} → ${status}.`); this.openTab('bookings'); },
      error: () => this.error('Changement de statut impossible.'),
    });
  }

  createActivity(): void {
    const payload = { ...this.newActivity, city: Number(this.newActivity.city), categories: this.newActivity.categories.map(Number) };
    this.admin.createActivity(payload).subscribe({
      next: (a: any) => { this.success(`Activité "${a.title}" créée.`); this.newSchedule.activity = a.id; },
      error: (e) => this.error('Création impossible : ' + JSON.stringify(e?.error ?? '')),
    });
  }

  createSchedule(): void {
    this.admin.createSchedule({ ...this.newSchedule, activity: Number(this.newSchedule.activity) }).subscribe({
      next: () => this.success('Créneau créé.'),
      error: (e) => this.error('Créneau impossible : ' + JSON.stringify(e?.error ?? '')),
    });
  }

  private success(msg: string) { this.feedbackType = 'success'; this.feedback = '✅ ' + msg; }
  private error(msg: string) { this.feedbackType = 'error'; this.feedback = msg; }
}
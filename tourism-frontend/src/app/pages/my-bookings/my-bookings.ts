import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { BookingService } from '../../services/booking.service';

@Component({
  selector: 'app-my-bookings',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './my-bookings.html',
  styleUrls: ['./my-bookings.css'],
})
export class MyBookingsPage implements OnInit {
  bookings: any[] = [];
  isLoading = false;
  feedback = '';
  feedbackType: 'success' | 'error' = 'success';

  constructor(private bookingService: BookingService) {}

  ngOnInit(): void {
    this.loadBookings();
  }

  loadBookings(): void {
    this.isLoading = true;
    this.bookingService.getBookings().subscribe({
      next: (response: any) => {
        this.bookings = Array.isArray(response) ? response : response?.results ?? [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.feedbackType = 'error';
        this.feedback = 'Impossible de charger vos réservations. Êtes-vous connecté ?';
      },
    });
  }

  cancel(booking: any): void {
    if (!confirm(`Annuler la réservation ${booking.booking_reference} ?`)) return;
    this.bookingService.cancelBooking(booking.id, 'Annulée par le client').subscribe({
      next: () => {
        this.feedbackType = 'success';
        this.feedback = '✅ Réservation annulée.';
        this.loadBookings();
      },
      error: () => {
        this.feedbackType = 'error';
        this.feedback = "Impossible d'annuler cette réservation.";
      },
    });
  }

  pay(booking: any): void {
    this.bookingService.payBooking(booking.id, { method: 'stripe', stripe_payment_intent_id: 'pi_demo_' + booking.id }).subscribe({
      next: () => {
        this.feedbackType = 'success';
        this.feedback = '✅ Paiement effectué, réservation confirmée.';
        this.loadBookings();
      },
      error: () => {
        this.feedbackType = 'error';
        this.feedback = 'Le paiement a échoué.';
      },
    });
  }
}
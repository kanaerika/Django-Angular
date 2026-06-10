import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { BookingService } from '../../services/booking.service';

@Component({
  selector: 'app-booking',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './booking.component.html',
  styleUrls: ['./booking.component.css'],
})
export class BookingComponent implements OnInit {

  bookingData = {
    schedule: '',
    number_of_travelers: 1,
    special_requests: ''
  };

  successMessage = '';
  errorMessage = '';
  isSubmitting = false;

  constructor(
    private bookingService: BookingService,
    private route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    const scheduleId = this.route.snapshot.queryParamMap.get('scheduleId');
    if (scheduleId) {
      this.bookingData.schedule = scheduleId;
    }
  }

  submitBooking() {
    if (!this.bookingData.schedule || this.bookingData.number_of_travelers < 1) {
      this.errorMessage = 'Le créneau et le nombre de voyageurs sont obligatoires.';
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.bookingService.createBooking({
      schedule: Number(this.bookingData.schedule),
      number_of_travelers: Number(this.bookingData.number_of_travelers),
      special_requests: this.bookingData.special_requests,
    }).subscribe({
      next: () => {
        this.successMessage = 'Réservation créée avec succès.';
        this.bookingData = { schedule: this.bookingData.schedule, number_of_travelers: 1, special_requests: '' };
      },
      error: (error: any) => {
        this.errorMessage = this.formatError(error);
      },
      complete: () => {
        this.isSubmitting = false;
      },
    });
  }

  private formatError(error: any): string {
    if (typeof error?.error === 'string') return error.error;
    if (error?.error?.detail) return error.error.detail;
    if (error?.error?.schedule) return Array.isArray(error.error.schedule) ? error.error.schedule[0] : error.error.schedule;
    if (error?.error?.number_of_travelers) return Array.isArray(error.error.number_of_travelers) ? error.error.number_of_travelers[0] : error.error.number_of_travelers;
    return 'Impossible de créer la réservation. Vérifiez les données envoyées.';
  }
}
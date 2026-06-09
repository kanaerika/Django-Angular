import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { BookingService } from '../../services/booking.service';

@Component({
  selector: 'app-booking',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './booking.component.html',
  styleUrls: ['./booking.component.css'],
})
export class BookingComponent {

  bookingData = {
    schedule: '',
    number_of_travelers: 1,
    special_requests: ''
  };

  successMessage = '';
  errorMessage = '';

  constructor(private bookingService: BookingService) {}

  submitBooking() {

    this.bookingService.createBooking(this.bookingData)
      .subscribe({
        next: (response: any) => {
          console.log(response);

          this.successMessage =
            'Booking created successfully';

          this.errorMessage = '';

          this.bookingData = {
            schedule: '',
            number_of_travelers: 1,
            special_requests: ''
          };
        },

       error: (error: any) => {
  console.log('BACKEND ERROR:', error);

  if (error.error) {
    this.errorMessage = JSON.stringify(error.error);
  } else {
    this.errorMessage = 'Unable to create booking';
  }
}
      });
  }
}
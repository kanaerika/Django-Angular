// src/app/services/booking.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class BookingService {

  private apiUrl = 'http://127.0.0.1:8000/api/bookings/bookings/';

  constructor(private http: HttpClient) {}

  createBooking(data: any): Observable<any> {
    return this.http.post(this.apiUrl, data);
  }

  getBookings(): Observable<any> {
    return this.http.get(this.apiUrl);
  }

  getMyStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}my-stats/`);
  }

  getUpcomingBookings(): Observable<any> {
    return this.http.get(`${this.apiUrl}upcoming/`);
  }

  getPastBookings(): Observable<any> {
    return this.http.get(`${this.apiUrl}past/`);
  }

  cancelBooking(id: number, reason?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}${id}/cancel/`, { reason });
  }

  payBooking(id: number, payload: { method: string; stripe_payment_intent_id?: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}${id}/pay/`, payload);
  }
}
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AdminService {
  private base = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  getStats(): Observable<any> { return this.http.get(`${this.base}/auth/dashboard/`); }

  listUsers(): Observable<any> { return this.http.get(`${this.base}/auth/users/`); }
  assignRole(userId: number, roleId: number): Observable<any> {
    return this.http.post(`${this.base}/auth/users/${userId}/assign-role/`, { role_id: roleId });
  }

  pendingReviews(): Observable<any> { return this.http.get(`${this.base}/reviews/reviews/pending/`); }
  moderateReview(id: number, isVisible: boolean): Observable<any> {
    return this.http.patch(`${this.base}/reviews/reviews/${id}/moderate/`, { is_visible: isVisible });
  }

  listBookings(): Observable<any> { return this.http.get(`${this.base}/bookings/bookings/`); }
  setBookingStatus(id: number, status: string): Observable<any> {
    return this.http.patch(`${this.base}/bookings/bookings/${id}/status/`, { status });
  }

  listCities(): Observable<any> { return this.http.get(`${this.base}/destinations/cities/`); }
  listCategories(): Observable<any> { return this.http.get(`${this.base}/tour/categories/`); }
  createActivity(payload: any): Observable<any> { return this.http.post(`${this.base}/tour/activities/`, payload); }
  createSchedule(payload: any): Observable<any> { return this.http.post(`${this.base}/tour/schedules/`, payload); }
}
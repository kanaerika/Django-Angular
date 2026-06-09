import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DashboardStats {
  user_count: number;
  role_count: number;
  profile_count: number;
  tour_count: number;
  booking_count: number;
  review_count: number;
  tourism_destination_count: number;
  hotel_count: number;
  hotel_booking_count: number;
  destination_review_count: number;
  country_count: number;
  city_count: number;
}

interface AuthResponse {
  access: string;
  refresh: string;
  user?: any;
}

interface RegisterResponse {
  message?: string;
  [key: string]: any;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiBaseUrl = 'http://127.0.0.1:8000/api/auth';

  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiBaseUrl}/login/`, {
      username: email,
      password,
    });
  }

  register(first_name: string, username: string, last_name: string, email: string, password: string, password2: string): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.apiBaseUrl}/users/`, {
      username,
      first_name,
      last_name,
      email,
      password,
      password2,
    });
  }

  refreshToken(refreshToken: string): Observable<{ access: string }> {
    return this.http.post<{ access: string }>('http://127.0.0.1:8000/api/token/refresh/', {
      refresh: refreshToken,
    });
  }

  getDashboard(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.apiBaseUrl}/dashboard/`, {
      headers: this.getAuthHeaders(),
    });
  }

  private getAuthHeaders(): HttpHeaders {
    const token = this.getAccessToken();
    return new HttpHeaders({
      Authorization: token ? `Bearer ${token}` : '',
    });
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}

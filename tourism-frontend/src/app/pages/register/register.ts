import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './register.html',
  styleUrls: ['./register.css']
})
export class Register implements OnInit, OnDestroy {

  showPassword: boolean = false;
  showconfirmPassword: boolean = false;
  isLoading: boolean = false;

  first_name: string = '';
  username: string ='';
  last_name: string = '';
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  successMessage: string = '';
  errorMessage: string = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  toggleRepeatPassword() {
    this.showconfirmPassword = !this.showconfirmPassword;
  }

  onSubmit() {
    if (!this.first_name|| !this.username|| !this.last_name || !this.email || !this.password || !this.confirmPassword) {
      alert('Please fill in all fields.');
      return;
    }

    if (this.password !== this.confirmPassword) {
      alert('Passwords do not match.');
      return;
    }

    if (this.password.length < 6) {
      alert('Password must be at least 6 characters long.');
      return;
    }

    this.isLoading = true;
    const registrationData = {
      first_name: this.first_name,
      username: this.username,
      last_name: this.last_name,
      email: this.email,
      password: this.password
    };

    console.log('Sending registration data:', registrationData);

    this.authService.register(this.first_name, this.username, this.last_name, this.email, this.password, this.confirmPassword).subscribe({
      next: (response) => {
        this.isLoading = false;
        console.log('Registration successful:', response);
        this.successMessage = '✅ Account created successfully! Redirecting to login...';
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Registration error:', error);
        console.error('Error response:', error?.error);
        console.error('Error status:', error?.status);
        
        let errorMessage = 'Registration failed. Please try again.';
        
        if (error?.error) {
          if (typeof error.error === 'string') {
            errorMessage = error.error;
          } else if (error.error.detail) {
            errorMessage = error.error.detail;
          } else if (error.error.message) {
            errorMessage = error.error.message;
          } else if (error.error.email) {
            errorMessage = `Email error: ${Array.isArray(error.error.email) ? error.error.email[0] : error.error.email}`;
          } else if (error.error.password) {
            errorMessage = `Password error: ${Array.isArray(error.error.password) ? error.error.password[0] : error.error.password}`;
          } else {
            errorMessage = JSON.stringify(error.error);
          }
        }
        
        this.errorMessage = errorMessage;
      }
    });
  }

  ngOnInit(): void {
    try { document.body.classList.add('hide-footer'); } catch {}
  }

  ngOnDestroy(): void {
    try { document.body.classList.remove('hide-footer'); } catch {}
  }

}
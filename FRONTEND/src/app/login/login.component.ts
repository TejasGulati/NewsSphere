import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {}

  onLogin(): void {
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
      this.authService.login(email, password).subscribe({
        next: () => {
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          this.errorMessage = this.getServerErrorMessage(error);
          setTimeout(() => {
            this.errorMessage = ''; // Clear the error message after 2 seconds
          }, 4000);
          console.error('Login error:', error);
        }
      });
    } else {
      this.errorMessage = this.getFormErrors(this.loginForm);
      setTimeout(() => {
        this.errorMessage = ''; // Clear the error message after 2 seconds
      }, 4000);
    }
  }

  // Extract detailed error messages
  private getFormErrors(form: FormGroup): string {
    const errorMessages: string[] = [];

    Object.keys(form.controls).forEach(controlName => {
      const control = form.get(controlName);
      if (control && control.errors) {
        Object.keys(control.errors).forEach(errorKey => {
          let errorMessage = '';
          switch (errorKey) {
            case 'required':
              errorMessage = `${this.capitalizeFirstLetter(controlName)} is required.`;
              break;
            case 'email':
              errorMessage = `The ${this.capitalizeFirstLetter(controlName)} provided is not a valid email address.`;
              break;
            default:
              errorMessage = `Invalid ${this.capitalizeFirstLetter(controlName)} value.`;
              break;
          }
          errorMessages.push(errorMessage);
        });
      }
    });

    return errorMessages.join(' ');
  }

  // Capitalize the first letter of a string
  private capitalizeFirstLetter(string: string): string {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  // Generate server error messages
  private getServerErrorMessage(error: any): string {
    switch (error.status) {
      case 400:
        return 'Incorrect login details. Please double-check your credentials.';
      case 401:
        return 'Unauthorized access. Ensure your email and password are correct.';
      case 403:
        return 'Access denied. You do not have permission to perform this action.';
      case 404:
        return 'Login service is not available. Please try again later.';
      case 500:
        return 'There was an issue with the server. Please try again later.';
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  }
}

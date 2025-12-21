import QRCode from 'qrcode';
import { logger } from './logger.js';

/**
 * Generate a QR code as a data URL
 * @param {string} text - The text/URL to encode
 * @param {object} options - QR code options
 * @returns {Promise<string>} - Data URL of the QR code image
 */
export async function generateQRCode(text, options = {}) {
  try {
    const defaultOptions = {
      errorCorrectionLevel: 'M',
      type: 'image/png',
      quality: 0.92,
      margin: 2,
      width: 256,
      color: {
        dark: '#000000',
        light: '#FFFFFF',
      },
      ...options,
    };

    const dataUrl = await QRCode.toDataURL(text, defaultOptions);
    return dataUrl;
  } catch (error) {
    logger.error('Error generating QR code:', error);
    throw error;
  }
}

/**
 * Generate a QR code as SVG
 * @param {string} text - The text/URL to encode
 * @param {object} options - QR code options
 * @returns {Promise<string>} - SVG string
 */
export async function generateQRCodeSVG(text, options = {}) {
  try {
    const defaultOptions = {
      errorCorrectionLevel: 'M',
      type: 'svg',
      margin: 2,
      width: 256,
      ...options,
    };

    const svg = await QRCode.toString(text, defaultOptions);
    return svg;
  } catch (error) {
    logger.error('Error generating QR code SVG:', error);
    throw error;
  }
}

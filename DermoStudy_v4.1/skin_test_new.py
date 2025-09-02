from ollama import chat
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
import sys

# --- La Tua Classe SkinStatus ---
class SkinStatus(BaseModel):
    """
    Represents the state of facial skin health, quantified through
    parameters analyzable via multi-wavelength image acquisition.
    All parameters are normalized to a specific range for easy comparison.
    """

    # --- Hydration and Skin Barrier ---
    hydration: float = Field(..., ge=0.0, le=1.0, 
        description="Skin hydration level (0.0 = very dry, 1.0 = optimally hydrated). "
                    "Measurable via spectral analysis of skin water content."
    )
    desquamation_index: float = Field(..., ge=0.0, le=1.0, 
        description="Desquamation index (0.0 = none, 1.0 = severe). "
                    "Measures the presence of dead cells and surface dryness. "
                    "Visible with magnification and various wavelengths."
    )
    barrier_integrity: float = Field(..., ge=0.0, le=1.0, 
        description="Skin barrier integrity (0.0 = compromised, 1.0 = intact). "
                    "Indirectly assessed from desquamation, irritation, and apparent permeability."
    )

    # --- Pigmentation and Complexion ---
    brightness: float = Field(..., ge=0.0, le=1.0, 
        description="General complexion brightness (0.0 = dull/lifeless, 1.0 = radiant/bright). "
                    "Derived from tone uniformity and light reflection."
    )
    pigmentation_uniformity: float = Field(..., ge=0.0, le=1.0, 
        description="Pigmentation uniformity (0.0 = many dyschromia/spots, 1.0 = very uniform complexion). "
                    "Analysis of color variations on the skin surface."
    )
    redness_index: float = Field(..., ge=0.0, le=1.0, 
        description="Redness index (0.0 = absent, 1.0 = very pronounced/erythema). "
                    "Quantifies the presence of diffuse or localized redness, visible capillaries. "
                    "Analyzable with hemoglobin-sensitive wavelengths."
    )
    melanin_spot_count: int = Field(..., ge=0, 
        description="Number of visible dark spots/hyperpigmentations (e.g., solar lentigines, post-inflammatory spots). "
                    "Quantifiable through image analysis."
    )

    # --- Texture and Pores ---
    smoothness: float = Field(..., ge=0.0, le=1.0, 
        description="Skin texture smoothness (0.0 = rough/irregular, 1.0 = very smooth/velvety). "
                    "Evaluation of superficial micro-topography."
    )
    pore_visibility: float = Field(..., ge=0.0, le=1.0, 
        description="Pore visibility (0.0 = very evident/enlarged, 1.0 = almost invisible/refined). "
                    "Quantifiable by average size and number of visible pores."
    )
    fine_lines_index: float = Field(..., ge=0.0, le=1.0, 
        description="Index of fine lines (not deep wrinkles) due to dehydration or slight loss of elasticity (0.0 = many, 1.0 = absent). "
                    "Analysis of superficial micro-depression."
    )
    
    # --- Sebum and Impurities ---
    oiliness: float = Field(..., ge=0.0, le=1.0, 
        description="Skin oiliness/shininess level (0.0 = matte, 1.0 = very shiny/oily). "
                    "Measurable via superficial light reflection."
    )
    comedone_count: int = Field(..., ge=0, 
        description="Number of visible comedones (blackheads and whiteheads) (0 = absent, >0 = present). "
                    "Quantifiable through image analysis."
    )
    imperfection_count: int = Field(..., ge=0, 
        description="Number of visible active imperfections (e.g., pimples, small inflammations). "
                    "Quantifiable through image analysis."
    )
    
    # --- Elasticity and Tone (indirect visual) ---
    elasticity_score: float = Field(..., ge=0.0, le=1.0, 
        description="Apparent elasticity score (0.0 = low, 1.0 = high). "
                    "Indirectly assessed by the skin's tendency to form folds or maintain shape after slight software/3D image-induced deformation."
    )
    
    # --- Sensitivity (visual indicators) ---
    sensibility_signs: float = Field(..., ge=0.0, le=1.0, 
        description="Visual signs of sensitivity (0.0 = absent, 1.0 = very present). "
                    "Includes redness, diffuse irritation, or visible reactivity to external stimuli (assessed pre/post exposure)."
    )
    
    # Corrected Validators for Pydantic V2
    @field_validator('hydration', 'brightness', 'desquamation_index', 'pigmentation_uniformity', 
                     'redness_index', 'smoothness', 'pore_visibility', 'fine_lines_index', 
                     'oiliness', 'elasticity_score', 'barrier_integrity', 'sensibility_signs')
    @classmethod # V2 validators require @classmethod
    def check_float_range(cls, v: float): # Type hint for 'v' is good practice
        if not (0.0 <= v <= 1.0):
            raise ValueError('Value must be between 0.0 and 1.0')
        return v
    
    @field_validator('melanin_spot_count', 'comedone_count', 'imperfection_count')
    @classmethod # V2 validators require @classmethod
    def check_non_negative_int(cls, v: int): # Type hint for 'v' is good practice
        if v < 0:
            raise ValueError('Value must be a non-negative integer')
        return v

    def get_overall_skin_score(self) -> float:
        """
        Calculates an overall skin health score.
        """
        weighted_sum = (
            self.hydration * 15 +
            self.barrier_integrity * 10 +
            self.brightness * 10 +
            self.pigmentation_uniformity * 8 +
            (1.0 - self.redness_index) * 12 +
            (1.0 - self.desquamation_index) * 8 +
            self.smoothness * 10 +
            (1.0 - self.pore_visibility) * 7 +
            (1.0 - self.fine_lines_index) * 5 +
            (1.0 - self.oiliness) * 5 +
            (1.0 - (self.comedone_count / 10.0)) * 5 + 
            (1.0 - (self.imperfection_count / 5.0)) * 5 + 
            self.elasticity_score * 5 +
            (1.0 - self.sensibility_signs) * 5
        )
        
        max_possible_weighted_score = 110.0
        
        overall_score = (weighted_sum / max_possible_weighted_score) * 100
        return max(0.0, min(100.0, overall_score))


# --- Classe per il Sommario della Pelle ---
class SkinSummary(BaseModel):
    summary: str = Field(..., description="Un sommario conciso e generale dello stato di salute della pelle del viso, basato sui parametri analizzati.")
    skin_status: SkinStatus = Field(..., description="Dettagliato stato di salute della pelle, quantificato.")


# --- Main Execution ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python skin_analysis.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    model_name = 'qwen2.5vl:latest'

    response = chat(
      model=model_name,
      format=SkinSummary.model_json_schema(),  # Passa lo schema di SkinSummary
      messages=[
        {
          'role': 'user',
          'content': (
            'Analizza l\'immagine del viso fornita per valutare lo stato di salute della pelle. '
            'Fornisci un riepilogo generale e dettagli numerici per ogni parametro della pelle, '
            'stimando i valori per idratazione, rossore, pori, ecc. come definiti nello schema. '
            'I valori dovrebbero essere da 0.0 a 1.0 per le percentuali e interi per i conteggi.'
          ),
          'images': [image_path],
        },
      ],
      options={'temperature': 0},
    )

    # Valida e stampa il risultato
    try:
        skin_analysis_result = SkinSummary.model_validate_json(response.message.content)
        
        print("--- Analisi dello Stato della Pelle del Viso ---")
        print(f"Sommario: {skin_analysis_result.summary}")
        
        skin = skin_analysis_result.skin_status
        print("\n--- Dettaglio Parametri ---")
        print(f"Idratazione: {skin.hydration:.2f}")
        print(f"Desquamazione: {skin.desquamation_index:.2f}")
        print(f"Integrità Barriera: {skin.barrier_integrity:.2f}")
        print(f"Luminosità: {skin.brightness:.2f}")
        print(f"Uniformità Pigmentazione: {skin.pigmentation_uniformity:.2f}")
        print(f"Rossore: {skin.redness_index:.2f}")
        print(f"Macchie Melaniniche: {skin.melanin_spot_count}")
        print(f"Levigatezza: {skin.smoothness:.2f}")
        print(f"Visibilità Pori: {skin.pore_visibility:.2f}")
        print(f"Linee Sottili: {skin.fine_lines_index:.2f}")
        print(f"Lucidità: {skin.oiliness:.2f}")
        print(f"Comedoni: {skin.comedone_count}")
        print(f"Imperfezioni: {skin.imperfection_count}")
        print(f"Elasticità: {skin.elasticity_score:.2f}")
        print(f"Segni Sensibilità: {skin.sensibility_signs:.2f}")
        
        overall_score = skin.get_overall_skin_score()
        print(f"\n--- Punteggio Complessivo Salute Pelle: {overall_score:.2f}/100 ---")

    except Exception as e:
        print(f"Si è verificato un errore nella validazione o nell'analisi: {e}")
        print(f"Contenuto raw della risposta: {response.message.content}")
// Supabase Edge Function - Face Verification
// Yüz tanıma servisi entegrasyonu (Azure Face API örneği)

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface VerificationRequest {
  referenceImageUrl: string
  verificationImageUrl: string
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
    )

    // Verify user is authenticated
    const { data: { user }, error: authError } = await supabaseClient.auth.getUser()
    if (authError || !user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    const { referenceImageUrl, verificationImageUrl }: VerificationRequest = await req.json()

    // Azure Face API Configuration
    const azureFaceKey = Deno.env.get('AZURE_FACE_API_KEY')
    const azureFaceEndpoint = Deno.env.get('AZURE_FACE_API_ENDPOINT')

    if (!azureFaceKey || !azureFaceEndpoint) {
      throw new Error('Face API credentials not configured')
    }

    // Detect faces in both images
    const detectFace = async (imageUrl: string) => {
      const response = await fetch(`${azureFaceEndpoint}/face/v1.0/detect`, {
        method: 'POST',
        headers: {
          'Ocp-Apim-Subscription-Key': azureFaceKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: imageUrl }),
      })
      return await response.json()
    }

    const [referenceFaces, verificationFaces] = await Promise.all([
      detectFace(referenceImageUrl),
      detectFace(verificationImageUrl),
    ])

    if (!referenceFaces[0]?.faceId || !verificationFaces[0]?.faceId) {
      return new Response(JSON.stringify({
        success: false,
        error: 'No face detected in one or both images',
        confidence: 0,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // Verify faces match
    const verifyResponse = await fetch(`${azureFaceEndpoint}/face/v1.0/verify`, {
      method: 'POST',
      headers: {
        'Ocp-Apim-Subscription-Key': azureFaceKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        faceId1: referenceFaces[0].faceId,
        faceId2: verificationFaces[0].faceId,
      }),
    })

    const verifyResult = await verifyResponse.json()

    return new Response(JSON.stringify({
      success: verifyResult.isIdentical,
      confidence: Math.round(verifyResult.confidence * 100),
      isIdentical: verifyResult.isIdentical,
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })

  } catch (error) {
    return new Response(JSON.stringify({
      error: error.message,
      success: false,
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})

